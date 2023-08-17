import json
from datetime import datetime, time
from typing import Any, List, Optional
from uuid import UUID

import dateutil.parser
import pydash as py_
from fastapi import APIRouter, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.chart import (
    get_chart_type1_data,
    get_chart_type2_data,
    get_chart_type3_data,
    get_filters,
)
from auo_project.core.constants import AdvanceChartType, ParameterType
from auo_project.core.recipe import (
    add_default_value_to_parameter,
    add_parameter_internal_value,
    add_recipe_value_to_parameter,
    get_chart_disease_z_options,
    get_chart_pulse_z_options,
    get_default_chart_settings,
    get_flat_parameter_dict,
    get_loaded_value,
    get_parameters,
    validate_chart_setting,
    validate_value,
    validate_values,
)
from auo_project.core.survey import get_days_range, get_survey_result, handle_s026
from auo_project.core.utils import safe_int, time_in_range
from auo_project.web.api import deps

router = APIRouter()


class PatchRecipeChartsInput(BaseModel):
    recipe_name: str = Field(min_length=1, max_length=50)
    analytical_params: schemas.RecipeAnalyticalParamsInput
    chart_settings: List[schemas.ChartSetting]


class ExportCSVInput(BaseModel):
    analytical_params: schemas.RecipeAnalyticalParamsInput
    chart_settings: List[schemas.ChartSetting]


class RecipeChartDataInput(schemas.RecipeAnalyticalParamsInput, schemas.ChartSetting):
    pass


def is_input_and_options_c006_match(survey_measure_answer, input_options):
    """
    c006	001	無
    c006	002	偶爾（1天/周）
    c006	003	經常（2-4天/周）
    c006	004	幾乎每天（5天以上/周）
    """

    if isinstance(survey_measure_answer, int) is False:
        return None
    for option_value in input_options:
        if option_value == "c006:001":
            if survey_measure_answer == 0:
                return True
        if option_value == "c006:002":
            if survey_measure_answer == 1:
                return True
        elif option_value == "c006:003":
            if survey_measure_answer >= 2 and survey_measure_answer <= 4:
                return True
        elif option_value == "c006:004":
            if survey_measure_answer >= 5:
                return True
    return False


def is_input_and_options_c009_match(survey_measure_answer, input_options):
    """
    c009	001	6:00~11:59		區段
    c009	002	12:00~17:59		區段
    c009	003	18:00~23:59		區段
    c009	004	00:00~05:59		區段
    """
    category_id = "c009"
    if isinstance(survey_measure_answer, time) is False:
        return None

    survey_measure_answer = time(
        survey_measure_answer.hour,
        survey_measure_answer.minute,
    )

    for option_value in input_options:
        if option_value == f"{category_id}:001":
            if survey_measure_answer >= time(6, 0) and survey_measure_answer <= time(
                11,
                59,
            ):
                return True
        elif option_value == f"{category_id}:002":
            if survey_measure_answer >= time(12, 0) and survey_measure_answer <= time(
                17,
                59,
            ):
                return True
        elif option_value == f"{category_id}:003":
            if survey_measure_answer >= time(18, 0) and survey_measure_answer <= time(
                23,
                59,
            ):
                return True
        elif option_value == f"{category_id}:004":
            if survey_measure_answer >= time(0, 0) and survey_measure_answer <= time(
                5,
                59,
            ):
                return True
    return False


def is_input_and_options_c010_match(survey_measure_answer, input_options):
    """
    c010	001	子時 23:00-00:59		十二時辰
    c010	002	丑時 01:00-02:59		十二時辰
    c010	003	寅時 03:00-04:59		十二時辰
    c010	004	卯時 05:00-06:59		十二時辰
    c010	005	辰時 07:00-08:59		十二時辰
    c010	006	已時 09:00-10:59		十二時辰
    c010	007	午時 11:00-12:59		十二時辰
    c010	008	未時 13:00-14:59		十二時辰
    c010	009	申時 15:00-16:59		十二時辰
    c010	010	酉時 17:00-18:59		十二時辰
    c010	011	戌時 19:00-20:59		十二時辰
    c010	012	亥時 21:00-22:59		十二時辰
    """
    category_id = "c010"
    if isinstance(survey_measure_answer, time) is False:
        return None

    survey_measure_answer = time(
        survey_measure_answer.hour,
        survey_measure_answer.minute,
    )

    init_start_hour = 23
    for option_value in input_options:
        for i in range(12):
            if option_value == f"{category_id}:00{i+1}":
                start_hour = (init_start_hour + 2 * i) % 24
                end_hour = (init_start_hour + 2 * i + 1) % 24
                start_time = time(start_hour, 0)
                end_time = time(end_hour, 59)
                if time_in_range(start_time, end_time, survey_measure_answer):
                    return True
    return False


def is_need_to_filter(measure: dict, key: str, val: dict):
    input_result = get_loaded_value(py_.get(val, "result"))
    component = py_.get(val, "component")
    measure_val = py_.get(measure, key)

    if isinstance(component, list) and len(component) > 0:
        component = component[0]
    if (
        measure_val is None
        or input_result == "all"
        or (isinstance(input_result, str) and ":000" in input_result)
    ):
        return False
    elif measure_val == input_result:
        return False
    elif component == "input":
        measure_val = safe_int(measure_val)
        input_result = safe_int(input_result)
        if (
            isinstance(measure_val, (int, float))
            and isinstance(input_result, (int, float))
            and measure_val >= input_result
        ):
            return False
        return True

    # TODO: check
    elif component in ["checkbox", "search_dialog", "multi_select_dialog"]:
        if (
            isinstance(measure_val, (int, float, time))
            and isinstance(input_result, list)
            and len(input_result) > 0
        ):

            if input_result[0].split(":")[0] == "c006":
                match = is_input_and_options_c006_match(measure_val, input_result)
                return match is False

            elif input_result[0].split(":")[0] == "c009":
                print("is_input_and_options_c009_match")
                match = is_input_and_options_c009_match(measure_val, input_result)
                return match is False

            elif input_result[0].split(":")[0] == "c010":
                print("is_input_and_options_c010_match")
                match = is_input_and_options_c010_match(measure_val, input_result)
                return match is False

        if measure_val == input_result:
            return False
        elif measure_val in input_result:
            return False
        elif isinstance(measure_val, list) and set(measure_val) & set(input_result):
            return False
    elif component == "calendar_date":
        dt_value = get_loaded_value(val["result"])
        if isinstance(dt_value, dict):
            input_dt = py_.get(measure, key, "")
            if dt_value["unit"] == "day":
                if (
                    input_dt[:10] >= dt_value["start"]
                    and input_dt[:10] <= dt_value["end"]
                ):
                    return False
            elif dt_value["unit"] == "hour":
                if isinstance(input_dt, str):
                    if time_in_range(
                        dt_value["start"],
                        dt_value["end"],
                        input_dt[11:16],
                    ):
                        return False
                elif isinstance(input_dt, time):
                    if time_in_range(dt_value["start"], dt_value["end"], input_dt):
                        return False

    return True


def get_blood_pressure_option(sbp: int, dbp: int):
    if sbp is None or dbp is None:
        return None
    if sbp < 90 and dbp < 60:
        return "c029:005"
    elif sbp < 130 and dbp < 85:
        return "c029:001"
    elif sbp >= 130 and sbp < 140 and dbp < 90:
        return "c029:002"
    elif sbp >= 140 and sbp < 160 and dbp < 100:
        return "c029:003"
    elif sbp >= 160 and dbp >= 100:
        return "c029:004"
    return None


def get_blood_pressure(measure_info):
    return get_blood_pressure_option(measure_info.sbp, measure_info.dbp)


async def get_z_options_dict(
    db_session: AsyncSession,
    parameters_input: schemas.RecipeAnalyticalParamsInput,
    analytical_unique_options: dict,
):
    p_types = [ParameterType.analytical]
    parameter_dict = await get_parameters(
        db_session=db_session,
        p_types=p_types,
        process_child_parent=False,
    )
    disease_options_dict = await crud.measure_disease_option.get_disease_options_dict(
        db_session=db_session,
    )
    # filter option = all
    z_options_dict = {}
    for key, value in parameter_dict.items():
        if key == "a001" and parameters_input.a001 != "all":
            loaded_value = json.loads(parameters_input.a001)
            z_options_dict[key] = [
                {"value": value, "label": value}
                for value in loaded_value.get("values", [])
            ]
        # 疾病史
        elif key == "a008" and parameters_input.a008 != "all":
            loaded_value = json.loads(parameters_input.a008)
            z_options_dict["a008"] = get_chart_disease_z_options(
                loaded_value,
                disease_options_dict,
            )
        # BCQ
        elif key == "a026":
            options = py_.get(value, "subField.options.1.subField.options")
            if parameters_input.a025 == "c056:001":
                z_options_dict[f"{key}:c056:001"] = options
            elif parameters_input.a025 == "c056:002":
                z_options_dict[f"{key}:c056:002"] = options

        # pulse condition
        elif key in ("a027"):
            if parameters_input.a027 != "all":
                loaded_value = json.loads(parameters_input.a027)
                options = py_.get(value, "subField.options.1.subField.options")
                pulse_options_dict = {option.get("value"): option for option in options}
                z_options_dict[key] = get_chart_pulse_z_options(
                    loaded_value,
                    pulse_options_dict,
                )
        # TODO: refactor
        elif key in ("a003", "a032"):
            options = py_.get(value, "subField.options")
            # 排除「不限」
            z_options_dict[key] = [
                option for option in options if ":000" not in option.get("value")
            ]

        # TODO: refactor
        else:
            options = py_.get(value, "subField.options.1.subField.options")
            if options:
                z_options_dict[key] = options

    print("z_options_dict", z_options_dict)
    for key, val in z_options_dict.items():
        parameter_id = key.split(":")[0]
        if hasattr(parameters_input, parameter_id):
            input_value = getattr(parameters_input, parameter_id)
            # filter selected options
            if input_value != "all" and ":000" not in input_value:
                if parameter_id == "a001":
                    dt_values = json.loads(input_value).get("values", [])
                    z_options_dict[key] = dt_values
                else:
                    selected = get_loaded_value(input_value)
                    selected = [selected] if isinstance(selected, str) else selected
                    z_options_dict[key] = [
                        option for option in val if option.get("value") in selected
                    ]
            # update options by analytical_unique_options
            else:
                specific_options = analytical_unique_options.get(key)
                if specific_options is not None:
                    z_options_dict[key] = [
                        option
                        for option in val
                        if option.get("value") in specific_options
                    ]

    return z_options_dict


async def get_filtered_measure_infos(
    db_session: AsyncSession,
    input_parameter_dict: dict,
    infos_dict: dict,
):
    import time

    start_time = time.time()
    survey_result = await get_survey_result()
    print(f"get_survey_result: {time.time() - start_time}")
    survey_dict_by_number = {x.number: x for x in survey_result}
    survey_number_list = [x.number for x in survey_result]
    measures = await crud.measure_info.get_by_numbers(
        db_session=db_session,
        list_ids=survey_number_list,
        # relations=["statistics"],
    )

    new_measures = []
    # add measure info
    for measure in measures:
        # TODO: add additional columns
        new_measure = {
            **survey_dict_by_number.get(measure.number, {}).dict(),
            **jsonable_encoder(measure),
        }
        # 新的資料都為空
        new_measure["p001"] = new_measure["proj_num"]
        new_measure["p002"] = new_measure["judge_dr"]
        # TODO: add 檢測單位
        # new_measure["p003"] =
        new_measure["p004"] = new_measure["measure_operator"]
        # TODO: advanced filter
        measure_time = dateutil.parser.isoparse(new_measure["measure_time"])
        new_measure["p005"] = new_measure["measure_time"]
        new_measure["p006"] = new_measure["survey_dt"]
        # TODO: fix 自訂 filter & add 區段 & 十二時成
        new_measure["p007"] = measure_time.time()
        # TODO: 新增欄位脈波通過率
        # new_measure["p008"] = new_measure["measure_time"]

        if new_measure["irregular_hr"] is True:
            new_measure["s022"] = "c050:002"
        else:
            new_measure["s022"] = "c050:001"

        s026 = handle_s026(new_measure["eat_at"], measure_time)
        if s026 is None:
            pass
        elif s026 < 2:
            new_measure["s026"] = "c033:001"
        elif s026 >= 2 and s026 < 4:
            new_measure["s026"] = "c033:002"
        elif s026 >= 4 and s026 < 7:
            new_measure["s026"] = "c033:003"
        elif s026 >= 7:
            new_measure["s026"] = "c033:004"

        s033 = get_days_range(new_measure["symptom_from"], measure_time)
        if s033 is None:
            pass
        elif s033 < 1:
            new_measure["s033"] = "c035:001"
        elif s033 >= 1 and s033 < 4:
            new_measure["s033"] = "c035:002"
        elif s033 >= 4 and s033 < 7:
            new_measure["s033"] = "c035:003"
        elif s033 >= 7:
            new_measure["s033"] = "c035:004"

        s037 = get_days_range(new_measure["covid_from"], measure_time)
        if s037 is None:
            pass
        elif s037 < 31:
            new_measure["s037"] = "c049:001"
        elif s037 >= 31 and s037 < 91:
            new_measure["s037"] = "c049:002"
        elif s037 >= 91 and s037 < 181:
            new_measure["s037"] = "c049:003"
        elif s037 >= 181:
            new_measure["s037"] = "c049:004"

        s040 = get_days_range(new_measure["menstruation_from"], measure_time)
        if s040 is None:
            pass
        elif s040 < 7:
            new_measure["s040"] = "c036:001"
        elif s040 >= 7 and s040 < 15:
            new_measure["s040"] = "c036:002"
        elif s040 >= 15 and s040 < 22:
            new_measure["s040"] = "c036:003"
        elif s040 >= 21 and s040 < 29:
            new_measure["s040"] = "c036:004"

        a028 = get_blood_pressure(measure_info=measure)
        new_measure["a028"] = a028

        new_measures.append(new_measure)
    # TODO: filter measure & survey
    filtered_measures = []

    for measure in new_measures:
        need_to_filter = False
        for key, val in infos_dict.items():
            # if key == "p007":
            # if key == "s001":
            #     print("debug", measure[key], val, input_parameter_dict[key])
            if is_need_to_filter(measure, key, val):
                print("filter", measure[key], val)
                need_to_filter = True
                break
        if need_to_filter is False:
            filtered_measures.append(measure)

    print("length", len(new_measures), len(filtered_measures))
    return filtered_measures


async def get_filtered_measure_statistics(db_session: AsyncSession):
    survey_result = await get_survey_result()
    survey_dict_by_number = {x.number: x for x in survey_result}
    survey_number_list = [x.number for x in survey_result]
    measures = await crud.measure_info.get_by_numbers(
        db_session=db_session,
        list_ids=survey_number_list,
        relations=["statistics"],
    )
    # TODO: filter measures by 主要特徵, 次要特徵 (measure or survey)
    measure_id_number_dict = {measure.id: measure.number for measure in measures}
    measure_id_dict = {measure.id: measure for measure in measures}
    measure_statistics = py_.flatten([measure.statistics for measure in measures])
    measure_statistics = [
        {
            **survey_dict_by_number.get(
                measure_id_number_dict.get(statistic.measure_id),
            ).dict(),
            **statistic.dict(),
            "a028": get_blood_pressure(measure_id_dict[statistic.measure_id]),
            "statistic_id": statistic.id,
            "measure_id": statistic.measure_id,
            "number": measure_id_number_dict.get(statistic.measure_id),
        }
        for statistic in measure_statistics
    ]
    return measure_statistics


@router.get("/parameter/basic")
async def get_basic_parameter(
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get basic parameters
    """
    if current_user.org.name != "x_medical_center":
        return {
            ParameterType.primary: [],
            ParameterType.secondary: [],
        }

    p_types = [ParameterType.primary, ParameterType.secondary]
    parameters = await get_parameters(db_session=db_session, p_types=p_types)
    for p_type in p_types:
        parameters[p_type.value] = add_default_value_to_parameter(
            parameters[p_type.value],
        )

    # add nested default value start
    flat_parameter_dict = get_flat_parameter_dict(parameters)
    flat_parameter_value_dict = {
        parameter_id: parameter.get("defaultValue")
        for parameter_id, parameter in flat_parameter_dict.items()
    }
    error_dict, infos_dict = await validate_values(
        db_session=db_session,
        parameters_input=schemas.RecipeBasicParameterInput(**flat_parameter_value_dict),
    )
    if error_dict:
        print("info_dict", infos_dict)
        raise HTTPException(422, detail=json.dumps(error_dict))

    for p_type in p_types:
        for parameter in parameters[p_type.value]:
            add_parameter_internal_value(parameter, infos_dict)
    # add nested default value end

    return parameters


@router.post("/parameter/basic", response_model=schemas.RecipeWithParamsResponse)
async def set_basic_parameter(
    parameters_input: schemas.RecipeBasicParameterInput,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
) -> Any:
    """
    Set basic parameters
    """
    # validate params
    error_dict, infos_dict = await validate_values(
        db_session=db_session,
        parameters_input=parameters_input,
    )
    if error_dict:
        raise HTTPException(422, detail=json.dumps(error_dict))

    owner_id = current_user.id
    recipe_in = schemas.RecipeCreate(
        owner_id=owner_id,
        name=None,
        stage="basic",
        subject_num_snapshot=None,
        snapshot_at=None,
        is_active=False,
    )

    recipe = await crud.recipe.create(db_session=db_session, obj_in=recipe_in)
    if not recipe:
        raise HTTPException(404, detail="recipe not found")

    recipe_parameter_in_list = []
    parameters_dict = parameters_input.dict(exclude_none=True)
    for key, value in parameters_dict.items():
        recipe_parameter_in_list.append(
            schemas.RecipeParameterCreate(
                recipe_id=recipe.id,
                parameter_id=key,
                value=str(value),
            ),
        )
    for recipe_parameter_in in recipe_parameter_in_list:
        await crud.recipe_parameter.create(
            db_session=db_session,
            obj_in=recipe_parameter_in,
            autocommit=False,
        )
    await db_session.commit()

    # TODO: run analytical preview
    # TODO: optimize save cache
    filtered_measure_infos = await get_filtered_measure_infos(
        db_session=db_session,
        input_parameter_dict=parameters_dict,
        infos_dict=infos_dict,
    )

    # multiple select
    specific_options_dict = {}
    analytical_keys = list(schemas.RecipeAnalyticalParamsInput.__fields__.keys())
    print("analytical_keys", analytical_keys)
    # print("a026c056001", )
    for question_id in analytical_keys:
        # TODO
        if question_id == "a001":  # 檢測日期
            pass
        elif question_id == "a002":  # 介入因子
            pass
        elif question_id == "a003":  # 生理性別
            pass
        # TODO
        elif question_id == "a008":  # 疾病史
            pass
        # TODO
        elif question_id == "a025":  # BCQ得分
            pass
        # TODO
        elif question_id == "a026":  # BCQ類型
            a026c056001 = py_.filter_(
                py_.uniq(py_.map_(filtered_measure_infos, "a026c056001")),
                lambda x: x is not None,
            )
            a026c056002 = py_.filter_(
                py_.uniq(py_.map_(filtered_measure_infos, "a026c056002")),
                lambda x: x is not None,
            )
            a026_union = sorted(list(set(a026c056001) | set(a026c056002)))
            if len(a026_union) > 0:
                specific_options_dict[question_id] = a026_union

        elif question_id == "a027":  # 二十八脈
            pass
        else:
            unique_values = py_.sort(
                py_.filter_(
                    py_.uniq(py_.map_(filtered_measure_infos, question_id)),
                    lambda x: x is not None,
                ),
            )
            if len(unique_values) > 0:
                specific_options_dict[question_id] = unique_values

    recipe_in = schemas.RecipeUpdate(
        subject_num_snapshot=len(filtered_measure_infos),
        analytical_unique_options=specific_options_dict,
        snapshot_at=datetime.now(),
    )
    recipe = await crud.recipe.update(
        db_session=db_session,
        obj_current=recipe,
        obj_new=recipe_in,
    )

    p_types = (ParameterType.analytical,)
    parameters_group = await get_parameters(
        db_session=db_session,
        p_types=p_types,
        specific_options_dict=specific_options_dict,
    )

    parameters_group["analytical"] = add_default_value_to_parameter(
        parameters_group["analytical"],
    )

    # add nested default value start
    flat_parameter_dict = get_flat_parameter_dict(parameters_group)
    flat_parameter_value_dict = {
        parameter_id: parameter.get("defaultValue")
        for parameter_id, parameter in flat_parameter_dict.items()
    }
    error_dict, infos_dict = await validate_values(
        db_session=db_session,
        parameters_input=schemas.RecipeAnalyticalParamsInput(
            **flat_parameter_value_dict
        ),
    )
    if error_dict:
        print("info_dict", infos_dict)
        raise HTTPException(422, detail=json.dumps(error_dict))

    for p_type in p_types:
        for parameter in parameters_group[p_type.value]:
            add_parameter_internal_value(parameter, infos_dict)

    # add nested default value end

    return schemas.RecipeWithAnalyticalParamsResponse(
        recipe=recipe,
        parameters=parameters_group,
    )


@router.get("/recipes/", response_model=List[schemas.RecipeRead])
async def get_recipes(
    db_session: AsyncSession = Depends(deps.get_db),
    name: Optional[str] = Query(None, title="範本名稱"),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    recipes = await crud.recipe.get_active_by_owner(
        db_session=db_session,
        owner_id=current_user.id,
    )
    if name:
        recipes = [r for r in recipes if r.name == name]
    return recipes


@router.get("/recipes/{recipe_id}", response_model=schemas.RecipeWithParamsResponse)
async def get_recipe(
    recipe_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    # TODO: add owner check
    recipe = await crud.recipe.get(db_session=db_session, id=recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe {recipe_id} not found")
    elif not recipe.is_active:
        raise HTTPException(status_code=400, detail=f"Recipe {recipe_id} is not active")

    p_types = (
        ParameterType.primary,
        ParameterType.secondary,
        ParameterType.analytical,
    )
    recipe_params_dict = await crud.recipe_parameter.get_dict_by_recipe_id(
        db_session=db_session,
        recipe_id=recipe_id,
    )
    parameters = await get_parameters(db_session=db_session, p_types=p_types)
    for p_type in p_types:
        parameters[p_type.value] = add_recipe_value_to_parameter(
            parameters[p_type.value],
            recipe_params_dict,
        )

    recipe_param_value_dict = {key: e.value for key, e in recipe_params_dict.items()}
    parameters_input = schemas.RecipeAllParameterInput(**recipe_param_value_dict)
    error_dict, infos_dict = await validate_values(
        db_session=db_session,
        parameters_input=parameters_input,
    )

    if error_dict:
        print("info_dict", infos_dict)
        raise HTTPException(422, detail=json.dumps(error_dict))

    for p_type in p_types:
        for parameter in parameters[p_type.value]:
            add_parameter_internal_value(parameter, infos_dict)

    # TODO: compare with previous options
    # TODO: add new random option setting (new option)
    # py_.set_(
    #     parameters,
    #     "parameters.analytical.3.subField.options.1.subField.options.1.is_new",
    #     True,
    # )
    # py_.set_(
    #     parameters,
    #     "parameters.analytical.3.subField.options.1.subField.options.2.is_new",
    #     True,
    # )
    # py_.set_(
    #     parameters,
    #     "parameters.parameters.3.subField.options.1.subField.options.3.is_new",
    #     True,
    # )
    # py_.set_(
    #     parameters,
    #     "parameters.analytical.6.subField.options.1.subField.options.5.is_new",
    #     True,
    # )

    return schemas.RecipeWithParamsResponse(recipe=recipe, parameters=parameters)


@router.patch("/recipes/{recipe_id}", response_model=schemas.RecipeRead)
async def update_recipe(
    body: PatchRecipeChartsInput,
    recipe_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    recipe = await crud.recipe.get(db_session=db_session, id=recipe_id)
    if not recipe:
        raise Exception(f"Recipe {recipe_id} not found")

    parameters_input = body.analytical_params
    error_dict, _ = await validate_values(
        db_session=db_session,
        parameters_input=parameters_input,
    )
    if error_dict:
        raise HTTPException(422, detail=json.dumps(error_dict))

    for chart_setting in body.chart_settings:
        validate_chart_setting(
            chart_setting=schemas.ChartSetting(**chart_setting.dict()),
        )

    chart_settings = [setting for setting in body.chart_settings if setting]

    other_same_name_recipe = await crud.recipe.get_by_name(
        db_session=db_session,
        name=body.recipe_name,
    )
    if other_same_name_recipe and other_same_name_recipe.id == recipe.id:
        other_same_name_recipe = None

    # there is a recipe with the same name
    if other_same_name_recipe:
        # make exist recipe inactive and rename it
        other_same_name_recipe_in = schemas.RecipeUpdate(
            name=f"{other_same_name_recipe.name}已被 id:{recipe.id} 覆蓋",
            is_active=False,
        )

        await crud.recipe.update(
            db_session=db_session,
            obj_current=other_same_name_recipe,
            obj_new=other_same_name_recipe_in,
            autocommit=True,
        )
        recipe_in = schemas.RecipeUpdate(
            name=body.recipe_name,
            stage="analytical",
            is_active=True,
            chart_settings=chart_settings,
        )
        recipe = await crud.recipe.update(
            db_session=db_session,
            obj_current=recipe,
            obj_new=recipe_in,
            autocommit=True,
        )

    # if the body name and recipe name are different, then create a new recipe
    elif recipe.is_active and recipe.name != body.recipe_name:
        recipe_basic_parameters = await crud.recipe_parameter.get_by_recipe_id(
            db_session=db_session,
            recipe_id=recipe.id,
        )
        recipe_in = schemas.RecipeCreate(
            owner_id=current_user.id,
            name=body.recipe_name,
            stage="analytical",
            is_active=True,
            subject_num_snapshot=recipe.subject_num_snapshot,
            snapshot_at=recipe.snapshot_at,
            chart_settings=chart_settings,
        )
        recipe = await crud.recipe.create(
            db_session=db_session,
            obj_in=recipe_in,
            autocommit=False,
        )
        for recipe_parameter in recipe_basic_parameters:
            # ignore analytical parameters
            if "a" in recipe_parameter.parameter_id:
                continue
            recipe_parameter_in = schemas.RecipeParameterCreate(
                recipe_id=recipe.id,
                parameter_id=recipe_parameter.parameter_id,
                value=recipe_parameter.value,
            )
            await crud.recipe_parameter.create(
                db_session=db_session,
                obj_in=recipe_parameter_in,
                autocommit=False,
            )
    else:
        recipe_in = schemas.RecipeUpdate(
            name=body.recipe_name,
            stage="analytical",
            is_active=True,
            chart_settings=chart_settings,
        )
        recipe = await crud.recipe.update(
            db_session=db_session,
            obj_current=recipe,
            obj_new=recipe_in,
            autocommit=False,
        )

    recipe_parameter_in_list = []
    parameters_dict = parameters_input.dict(exclude_none=True)
    for key, value in parameters_dict.items():
        recipe_parameter_in_list.append(
            schemas.RecipeParameterCreate(
                recipe_id=recipe.id,
                parameter_id=key,
                value=str(value),
            ),
        )
    for recipe_parameter_in in recipe_parameter_in_list:
        recipe_param = await crud.recipe_parameter.get_recipe_parameter(
            db_session=db_session,
            recipe_id=recipe_parameter_in.recipe_id,
            parameter_id=recipe_parameter_in.parameter_id,
        )
        if recipe_param:
            recipe_parameter_update_in = schemas.RecipeParameterUpdate(
                value=recipe_parameter_in.value,
            )
            await crud.recipe_parameter.update(
                db_session=db_session,
                obj_current=recipe_param,
                obj_new=recipe_parameter_update_in,
                autocommit=False,
            )
        else:
            await crud.recipe_parameter.create(
                db_session=db_session,
                obj_in=recipe_parameter_in,
                autocommit=False,
            )

    await db_session.commit()

    return recipe


@router.post(
    "/recipes/{recipe_id}/parameter/analytical",
    response_model=schemas.RecipeWithChartsResponse,
)
async def get_analytical_result(
    parameters_input: schemas.RecipeAnalyticalParamsInput,
    recipe_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    recipe = await crud.recipe.get(db_session=db_session, id=recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe {recipe_id} not found")
    elif recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail=f"Recipe {recipe_id} is not owned by you",
        )

    error_dict, _ = await validate_values(
        db_session=db_session,
        parameters_input=parameters_input,
    )
    if error_dict:
        raise HTTPException(422, detail=json.dumps(error_dict))

    # TODO: calculate analytical result

    # handle select "all" then filter z options: a001, a008, a027, a030
    def process_z_options_by_selected_option(z_options, parameters_input):
        # TODO: hide z option: 介入因子、血壓 for demo
        block_z_options = ["a002"]
        # 檢測日期
        if parameters_input.a001 == "all":
            block_z_options.append("a001")
        # 疾病史
        if parameters_input.a008 == "all":
            block_z_options.append("a008")
        # 二十八脈
        if parameters_input.a027 == "all":
            block_z_options.append("a027")
        # 居住縣市
        if parameters_input.a030 == "all":
            block_z_options.append("a030")
        block_z_options.append("a025")
        block_z_options.append("a026")
        return [
            z_option
            for z_option in z_options
            if z_option["value"] not in block_z_options
        ]

    z_options = await crud.measure_parameter.get_options_by_p_type(
        db_session=db_session,
        p_type=ParameterType.analytical,
    )
    z_options = process_z_options_by_selected_option(z_options, parameters_input)
    # filter：BCQ 類型 - 一般、BCQ類型 - 正規化
    if parameters_input.a025 != "all":
        if parameters_input.a025 == "c056:001":
            z_options.append({"value": "a026:c056:001", "label": "BCQ 類型 - 一般"})
        elif parameters_input.a025 == "c056:002":
            z_options.append({"value": "a026:c056:002", "label": "BCQ 類型 - 正規化"})
    z_options = sorted(z_options, key=lambda x: x["value"])

    default_chart_settings = get_default_chart_settings()
    chart_settings = (
        recipe.chart_settings if recipe.chart_settings else default_chart_settings
    )

    filters = get_filters()
    filters.append({"type": "feature", "options": z_options})

    return schemas.RecipeWithChartsResponse(
        recipe=recipe,
        charts=schemas.Chart(settings=chart_settings, filters=filters),
    )


@router.post("/recipes/{recipe_id}/chart")
async def get_chart_data(
    chart_input: RecipeChartDataInput,
    recipe_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    recipe = await crud.recipe.get(db_session=db_session, id=recipe_id)
    if not recipe:
        raise Exception(f"Recipe {recipe_id} not found")

    parameters_input = schemas.RecipeAnalyticalParamsInput(**chart_input.dict())
    error_dict, infos_dict = await validate_values(
        db_session=db_session,
        parameters_input=parameters_input,
    )
    if error_dict:
        raise HTTPException(422, detail=json.dumps(error_dict))

    z_options_dict = await get_z_options_dict(
        db_session,
        parameters_input,
        recipe.analytical_unique_options or {},
    )

    validate_chart_setting(
        schemas.ChartSetting(
            chart_type=chart_input.chart_type,
            x=chart_input.x,
            y=chart_input.y,
            z=chart_input.z,
        ),
    )

    result = None
    if chart_input.chart_type == AdvanceChartType.parameter_six_pulse:
        x_options = "l_cu,l_qu,l_ch,r_cu,r_qu,r_ch".split(",")
        z_options = z_options_dict.get(chart_input.z, [])
        # z_labels = get_labels(z_options)
        domain = chart_input.y.get("domain")

        # TODO: filter primary and secondary
        table_column = chart_input.y["domain"][-1].lower()
        if "/" in table_column:
            table_column = table_column.replace("/", "_div_")
        elif ":" in table_column:
            table_column = table_column.split(":")[-1]

        statisitc_filter = "MEAN"
        if "cv" in table_column:
            statisitc_filter = "CV"
            table_column = table_column.replace("cv", "")
        if table_column == "pr":
            table_column = "hr"

        hand_map = {"Left": "左", "Right": "右"}
        position_map = {"Cu": "寸", "Qu": "關", "Ch": "尺"}

        # TODO: change get_filtered_measure_infos
        measure_statistics = await get_filtered_measure_statistics(
            db_session=db_session,
        )
        measure_statistics = [
            {
                **statistic,
                "x_label": hand_map.get(py_.get(statistic, "hand"), "")
                + position_map.get(py_.get(statistic, "position"), ""),
                "x": f"{ py_.get(statistic, 'hand').lower()[0]}_{py_.get(statistic, 'position').lower()}",
                "y": py_.get(statistic, table_column),
            }
            for statistic in measure_statistics
            if py_.get(statistic, "statistic").upper() == statisitc_filter.upper()
        ]
        # print("measure_statistics", measure_statistics)
        test = py_.group_by(
            [
                {
                    "y": e["y"],
                    "measure_id": e["measure_id"],
                    "a026c056001": e["a026c056001"],
                }
                for e in measure_statistics
            ],
            "a026c056001",
        )

        print("test", type(test), test.keys(), test)

        result = get_chart_type1_data(
            x_options,
            chart_input.y["domain"][-1],
            chart_input.z,
            z_options,
            sdata=measure_statistics,
        )

    elif chart_input.chart_type == AdvanceChartType.parameter_cross:
        table_column = chart_input.y["domain"][-1].lower()
        if "/" in table_column:
            table_column = table_column.replace("/", "_div_")
        elif ":" in table_column:
            table_column = table_column.split(":")[-1]

        statisitc_filter = "MEAN"
        if "cv" in table_column:
            statisitc_filter = "CV"
            table_column = table_column.replace("cv", "")
        if table_column == "pr":
            table_column = "hr"

        # TODO: check whether filter pass rate
        def normalize_parameter_name(name):
            # replace ':' for a026:c056:001 and a026:c056:002
            if isinstance(name, str):
                return name.replace(":", "")

        measure_statistics = await get_filtered_measure_statistics(
            db_session=db_session,
        )
        measure_statistics = [
            {
                **statistic,
                "x": py_.get(
                    statistic,
                    normalize_parameter_name(chart_input.x),
                ),
                "y": py_.get(statistic, table_column),
            }
            for statistic in measure_statistics
            if py_.get(statistic, "statistic") == statisitc_filter
        ]

        x_options = z_options_dict.get(chart_input.x, [])
        z_options = z_options_dict.get(chart_input.z, [])
        # z_labels = get_labels(z_options)
        domain = chart_input.y.get("domain")
        six_pulse = chart_input.y.get("six_pulse")
        domain_last = domain[-1]
        result = get_chart_type2_data(
            chart_input.x,
            x_options,
            domain_last,
            six_pulse,
            chart_input.z,
            z_options,
            sdata=measure_statistics,
        )

    elif chart_input.chart_type == AdvanceChartType.six_pulse_cn:
        x_options = [f"C{i}" for i in range(1, 12)]
        z_options = z_options_dict.get(chart_input.z, [])
        # z_labels = get_labels(z_options)
        six_pulse = chart_input.y.get("six_pulse")
        hand_lc = six_pulse.split("_")[0]
        position_lc = six_pulse.split("_")[1]
        statistics = chart_input.y.get("statistics")
        statisitc_filter = statistics.upper()

        measure_statistics = await get_filtered_measure_statistics(
            db_session=db_session,
        )
        measure_statistics = [
            statistic
            for statistic in measure_statistics
            if py_.get(statistic, "statistic") == statisitc_filter
            and py_.get(statistic, "hand").lower()[0] == hand_lc
            and py_.get(statistic, "position").lower() == position_lc
        ]

        result = get_chart_type3_data(
            x_options,
            six_pulse,
            statistics,
            chart_input.z,
            z_options,
            sdata=measure_statistics,
        )

    return result


@router.post("/export/{recipe_id}/csv")
async def export_csv(
    body: ExportCSVInput,
    recipe_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    recipe = await crud.recipe.get(db_session=db_session, id=recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    parameters_input = body.analytical_params
    error_dict, _ = await validate_values(
        db_session=db_session,
        parameters_input=parameters_input,
    )
    if error_dict:
        raise HTTPException(422, detail=json.dumps(error_dict))

    for chart_setting in body.chart_settings:
        validate_chart_setting(
            chart_setting=schemas.ChartSetting(**chart_setting.dict()),
        )

    chart_settings = [setting for setting in body.chart_settings if setting]
    return FileResponse(
        path="/app/src/多人多次下載檔案範例.zip",
        filename="多人多次下載檔案範例.zip",
        headers={"Access-Control-Expose-Headers": "Content-Disposition"},
    )


@router.get("/test")
async def test3(db_session: AsyncSession = Depends(deps.get_db)):
    p_types = [ParameterType.primary, ParameterType.secondary, ParameterType.analytical]
    parameter_dict = await get_parameters(
        db_session=db_session,
        p_types=p_types,
        process_child_parent=False,
    )
    disease_options_dict = await crud.measure_disease_option.get_disease_options_dict(
        db_session=db_session,
    )
    # create tests for function validate_value
    # test 1: valid value
    parameter_id = "p001"
    value = "all"
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == "all"
    assert path == {"path": ".subField.options.0", "component": "radio"}

    # valid value
    parameter_id = "p001"
    proj_num_values = await crud.measure_info.get_proj_num(db_session=db_session)
    value = json.dumps([e["value"] for e in proj_num_values])
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {
        "path": [
            ".subField.options.1.subField.options.0",
            ".subField.options.1.subField.options.1",
            ".subField.options.1.subField.options.2",
        ],
        "component": ["search_dialog", "search_dialog", "search_dialog"],
    }

    # test 2: invalid value
    parameter_id = "p001"
    value = "custom"
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == "value cannot be custom"

    parameter_id = "p001"
    value = "123"
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"the value {value} is not found"

    parameter_id = "p001"
    value = '["1","2","3"]'
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"some elements of {value} are not align with option values"

    parameter_id = "p001"
    value = "abc"
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"the value {value} is not found"

    parameter_id = "s001"
    value = "all"
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == "all"
    # assert path == {'path': 'subField.options.0', 'component': 'radio'}

    parameter_id = "s001"
    value = json.dumps(["c002:001", "c002:002", "c002:003"])
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {
        "path": [
            ".subField.options.1.subField.options.0",
            ".subField.options.1.subField.options.1",
            ".subField.options.1.subField.options.2",
        ],
        "component": ["checkbox", "checkbox", "checkbox"],
    }

    # checkbox
    parameter_id = "s001"
    value = json.dumps(["c002:001", "c002:002", "c002:099"])
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"some value is not found: c002:099"

    # input
    parameter_id = "s008"
    value = "1"
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {"path": ".subField.options.1.subField", "component": "input"}

    # calendar_date / day: valid
    parameter_id = "p006"
    value = json.dumps({"unit": "day", "start": "2021-01-01", "end": "2021-01-31"})
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {
        "path": ".subField.options.1.subField",
        "component": "calendar_date",
    }

    # calendar_date / day: not found
    parameter_id = "p005"
    value = json.dumps({"unit": "day", "start": "2021-01-01", "end": "2021-01-31"})
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == "the value is belong to hour but there is no component in it"

    # calendar_date / day: start > end
    parameter_id = "p005"
    loaded_value = {"unit": "day", "start": "2021-02-01", "end": "2021-01-31"}
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert (
            str(e)
            == f"start: {loaded_value['start']} is greater than end: {loaded_value['end']}"
        )

    # hour: valid
    parameter_id = "s005"
    loaded_value = {"unit": "hour", "start": "09:00", "end": "18:00"}
    value = json.dumps(loaded_value)
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {
        "path": ".subField.options.1.subField.options.2.subField",
        "component": "calendar_date",
    }

    # hour: invalid
    parameter_id = "s005"
    loaded_value = {"unit": "hour", "start": "99:00", "end": "18:00"}
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert (
            str(e)
            == f"{loaded_value['start']} or {loaded_value['end']} is not valid hour format (HH:MM)"
        )

    # hour: invalid
    parameter_id = "s005"
    loaded_value = {"unit": "hour", "start": "19:00", "end": "18:00"}
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert (
            str(e)
            == f"start: {loaded_value['start']} is greater than end: {loaded_value['end']}"
        )

    # measure_date_or_month: valid
    parameter_id = "a001"
    value = json.dumps(
        {"unit": "day", "values": ["2021-01-01", "2021-01-31", "2021-02-01"]},
    )
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {
        "path": ".subField.options.1.subField",
        "component": "measure_date_or_month",
    }

    # measure_date_or_month: invalid
    parameter_id = "a001"
    loaded_value = {"unit": "day", "values": ["2021-01-40", "2021-01-31", "2021-02-01"]}
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert (
            str(e)
            == f"values: {loaded_value['values']} is not valid date format (YYYY-MM-DD)"
        )

    # measure_date_or_month: month valid
    parameter_id = "a001"
    value = json.dumps({"unit": "month", "values": ["2021-01", "2021-02", "2021-03"]})
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value

    # measure_date_or_month: month invalid
    parameter_id = "a001"
    value = json.dumps({"unit": "month", "values": ["2021-01", "2021-02", "2021-03"]})
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value

    # measure_date_or_month: month invalid
    parameter_id = "a001"
    loaded_value = {"unit": "month", "values": ["2021-01", "2021-02-01", "2021-03"]}
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert (
            str(e)
            == f"values: {loaded_value['values']} is not valid month format (YYYY-MM)"
        )

    # group
    parameter_id = "s023"
    value = "c022:999"
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == "the input parameter should not be group"

    # radio valid
    parameter_id = "s022"
    value = "c050:000"
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {"path": ".subField.options.0", "component": "radio"}

    # radio invalid
    parameter_id = "s022"
    value = "c050:999"
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"the value {value} is not found"

    # dropdown
    # dropdown valid
    parameter_id = "p008"
    value = "c001:009"
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {
        "path": ".subField.options.1.subField.options.8",
        "component": "dropdown",
    }

    # dropdown invalid
    parameter_id = "p008"
    value = "c001:999"
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"the value {value} is not found"

    # disease single valid
    parameter_id = "a008"
    loaded_value = ["d001:003", "d001:002", "d001:007", "d004:002", "d004:009"]
    value = json.dumps(loaded_value)
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {
        "path": ".subField.options.1.subField",
        "component": "multi_select_dialog_disease_single",
    }

    # disease single invalid
    parameter_id = "a008"
    loaded_value = ["d001:003", "d001:002", "d001:007", "d004:002", "c004:001"]
    invalid_values = ["c004:001"]
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"values: {invalid_values} are not belong to disease options"

    # disease single invalid
    parameter_id = "a008"
    loaded_value = ["d001:003", "d001:002", "d001:007", "d004:002", "d004:999"]
    invalid_values = ["d004:999"]
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"values: {invalid_values} are not belong to disease options"

    # disease crosss valid
    parameter_id = "a008"
    loaded_value = [
        {
            "include": ["d001:001"],
            "exclude": ["d001:003", "d001:002", "d001:007", "d004:002", "d004:009"],
        },
    ]
    value = json.dumps(loaded_value)
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {
        "path": ".subField.options.2.subField",
        "component": "multi_select_dialog_disease_cross",
    }
    # disease crosss invalid
    parameter_id = "a008"
    loaded_value = [
        {
            "include": ["d001:001", "d001:002"],
            "exclude": ["d001:003", "d001:002", "d001:007", "d004:002", "d004:009"],
        },
    ]
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == "include disease only accpets one value"

    # disease crosss invalid
    parameter_id = "a008"
    loaded_value = [
        {
            "include": ["d004:999"],
            "exclude": [
                "d001:003",
                "d001:002",
                "d001:007",
                "d004:002",
                "d004:009",
                "d004:010",
            ],
        },
    ]
    invalid_values = ["d004:999"]
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"values: {invalid_values} are not belong to disease options"

    # disease crosss invalid
    parameter_id = "a008"
    loaded_value = [
        {
            "include": ["d004:000"],
            "exclude": [
                "d001:003",
                "d001:002",
                "d001:007",
                "d004:002",
                "d004:009",
                "d004:010",
                "d010:100",
                "d011:100",
            ],
        },
    ]
    invalid_values = ["d010:100", "d011:100"]
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"values: {invalid_values} are not belong to disease options"

    # disease crosss invalid
    parameter_id = "a008"
    loaded_value = [
        {
            "include": ["d004:000"],
            "exclude": [
                "d001:003",
                "d001:002",
                "d001:007",
                "d004:002",
                "d004:009",
                "d004:010",
                "d010:100",
                "d011:100",
            ],
        },
        {
            "include": ["d004:000"],
            "exclude": [
                "d001:003",
                "d001:002",
                "d001:007",
                "d004:002",
                "d004:009",
                "d004:010",
                "d010:100",
                "d011:100",
            ],
        },
    ]
    invalid_values = ["d010:100", "d011:100"]
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"values: {invalid_values} are not belong to disease options"

    parameter_id = "a008"
    loaded_value = [
        {
            "include": ["d004:000"],
            "exclude": [
                "d001:003",
                "d001:002",
                "d001:007",
                "d004:002",
                "d004:009",
                "d004:010",
                "d010:100",
                "d011:100",
            ],
        },
        {
            "include": ["d004:000"],
            "exclude": [
                "d001:003",
                "d001:002",
                "d001:007",
                "d004:002",
                "d004:009",
                "d004:010",
                "d010:100",
                "d011:100",
            ],
        },
        {
            "include": ["d004:000"],
            "exclude": [
                "d001:003",
                "d001:002",
                "d001:007",
                "d004:002",
                "d004:009",
                "d004:010",
                "d010:100",
                "d011:100",
            ],
        },
        {
            "include": ["d004:000"],
            "exclude": [
                "d001:003",
                "d001:002",
                "d001:007",
                "d004:002",
                "d004:009",
                "d004:010",
                "d010:100",
                "d011:100",
            ],
        },
        {
            "include": ["d004:000"],
            "exclude": [
                "d001:003",
                "d001:002",
                "d001:007",
                "d004:002",
                "d004:009",
                "d004:010",
                "d010:100",
                "d011:100",
            ],
        },
        {
            "include": ["d004:000"],
            "exclude": [
                "d001:003",
                "d001:002",
                "d001:007",
                "d004:002",
                "d004:009",
                "d004:010",
                "d010:100",
                "d011:100",
            ],
        },
    ]
    invalid_values = ["d010:100", "d011:100"]
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == "cross disease params should be less than 6"

    # multi_select_dialog_pulse_condition_single valid
    parameter_id = "a027"
    loaded_value = ["c028:001", "c028:022", "c028:028"]
    value = json.dumps(loaded_value)
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {
        "path": ".subField.options.1.subField.component",
        "component": "multi_select_dialog_pulse_condition_single",
    }

    # multi_select_dialog_pulse_condition_single invalid
    parameter_id = "a027"
    loaded_value = ["c028:001", "c028:022", "c028:900", "c028:999"]
    invalid_values = ["c028:900", "c028:999"]
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"values: {invalid_values} are not belong to disease options"

    # multi_select_dialog_pulse_condition_cross valid
    parameter_id = "a027"
    loaded_value = [
        ["c028:001"],
        ["c028:001", "c028:022"],
        ["c028:001", "c028:022", "c028:028"],
    ]
    value = json.dumps(loaded_value)
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value
    assert path == {
        "path": ".subField.options.2.subField.component",
        "component": "multi_select_dialog_pulse_condition_cross",
    }

    # multi_select_dialog_pulse_condition_cross invalid
    parameter_id = "a027"
    loaded_value = [
        ["c028:001"],
        ["c028:001", "c028:022", "c028:099"],
        ["c028:001", "c028:022", "c028:028"],
    ]
    invalid_values = ["c028:099"]
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == f"values: {invalid_values} are not belong to disease options"

    # multi_select_dialog_pulse_condition_cross invalid
    parameter_id = "a027"
    loaded_value = [
        ["c028:001"],
        ["c028:001", "c028:022", "c028:099"],
        ["c028:001", "c028:022", "c028:028"],
        ["c028:026"],
    ]
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == "cross pulse condition params length should be less than 4"

    # multi_select_dialog_pulse_condition_cross invalid
    parameter_id = "a027"
    loaded_value = []
    value = json.dumps(loaded_value)
    try:
        result, path = await validate_value(
            parameter_id=parameter_id,
            value=value,
            parameter_options_dict=parameter_dict,
            disease_options_dict=disease_options_dict,
        )
    except ValueError as e:
        assert str(e) == "cross pulse condition params length should be more than 0"

    return "ok"
