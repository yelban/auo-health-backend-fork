import json
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, models, schemas
from auo_project.core.constants import ParameterType
from auo_project.core.mock import get_mock_chart_data
from auo_project.core.recipe import (
    add_default_value_to_parameter,
    add_recipe_value_to_parameter,
    get_parameters,
    validate_value,
)
from auo_project.web.api import deps

router = APIRouter()


class PatchRecipeChartsInput(BaseModel):
    recipe_name: str
    # analytical_params: schemas.RecipeAnalyticalParamsInput
    charts_setting: List[Dict[str, Any]]


async def validate_values(
    db_session: AsyncSession,
    parameters_input: schemas.RecipeBasicParameterInput,
):

    p_types = [ParameterType.primary, ParameterType.secondary, ParameterType.analytical]
    error_msg = ""
    error_dict = {}
    parameter_dict = await get_parameters(
        db_session=db_session,
        p_types=p_types,
        process_child_parent=False,
    )
    disease_options_dict = await crud.measure_disease_option.get_disease_options_dict(
        db_session=db_session,
    )
    for parameter_id, value in parameters_input.dict().items():
        try:
            result, path = await validate_value(
                parameter_id=parameter_id,
                value=value,
                parameter_options_dict=parameter_dict,
                disease_options_dict=disease_options_dict,
            )
        except ValueError as e:
            error_msg += f"Parameter {parameter_id} has invalid value {value}.\n"
            error_dict[parameter_id] = str(e)

    return error_dict


@router.get("/test3")
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

    parameter_id = "s001"
    value = json.dumps(["c002:001", "c002:002", "c002:003"])
    result, path = await validate_value(
        parameter_id=parameter_id,
        value=value,
        parameter_options_dict=parameter_dict,
        disease_options_dict=disease_options_dict,
    )
    assert result == value

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

    # TODO: pulse_condition single
    # TODO: pulse_condition cross

    return "ok"


@router.get("/test")
async def test(
    db_session: AsyncSession = Depends(deps.get_db),
):
    recipe_params = await crud.recipe_parameter.get_by_recipe_id(
        db_session=db_session,
        recipe_id="620be11a-2620-4198-8039-6a8198cc7acb",
    )
    recipe_params_dict = dict([(p.parameter_id, p.value) for p in recipe_params])
    parameters_input = schemas.RecipeBasicParameterInput(**recipe_params_dict)
    error_dict = await validate_values(
        db_session=db_session,
        parameters_input=parameters_input,
    )
    if error_dict:
        raise HTTPException(422, detail=json.dumps(error_dict))

    return True


@router.get("/parameter/basic/new")
async def get_basic_parameter_analytic(
    db_session: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get basic parameters
    """
    p_types = [ParameterType.analytical]
    parameters = await get_parameters(db_session=db_session, p_types=p_types)
    p_types = parameters.keys()
    for p_type in p_types:
        parameters[p_type] = add_default_value_to_parameter(parameters[p_type])
    return parameters


@router.get("/parameter/basic")
async def get_basic_parameter(
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get basic parameters
    """
    p_types = [ParameterType.primary, ParameterType.secondary]
    parameters = await get_parameters(db_session=db_session, p_types=p_types)
    p_types = parameters.keys()
    for p_type in p_types:
        parameters[p_type] = add_default_value_to_parameter(parameters[p_type])
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
    error_dict = await validate_values(
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

    recipe_parameter_in_list = []
    parameters_dict = parameters_input.dict(exclude_none=True)
    for key, value in parameters_dict.items():
        # TODO: check key and value valid
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
    db_session.commit()

    # TODO: run analytical preview
    from random import randint

    recipe_in = schemas.RecipeUpdate(
        subject_num_snapshot=randint(100, 500),
        snapshot_at=datetime.now(),
    )
    recipe = await crud.recipe.update(
        db_session=db_session,
        obj_current=recipe,
        obj_new=recipe_in,
    )

    p_types = (ParameterType.analytical,)
    parameters_group = await get_parameters(db_session=db_session, p_types=p_types)

    parameters_group["analytical"] = add_default_value_to_parameter(
        parameters_group["analytical"],
    )
    return schemas.RecipeWithAnalyticalParamsResponse(
        recipe=recipe,
        parameters=parameters_group,
    )


@router.get("/recipes/", response_model=List[schemas.RecipeRead])
async def get_recipes(
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
    # TODO: add current_user
    # owner_id = current_user.id
    owner_id = "24a8dd68-f304-4eb6-b7ed-c6978943d090"
    recipes = await crud.recipe.get_active_by_owner(
        db_session=db_session,
        owner_id=owner_id,
    )
    return recipes


@router.get("/recipes/{recipe_id}", response_model=schemas.RecipeWithParamsResponse)
async def get_recipe(
    recipe_id: UUID,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    ip_allowed: bool = Depends(deps.get_ip_allowed),
):
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
    print("recipe_params_dict", recipe_params_dict)
    parameters = await get_parameters(db_session=db_session, p_types=p_types)
    for p_type in p_types:
        parameters[p_type.value] = add_recipe_value_to_parameter(
            parameters[p_type.value],
            recipe_params_dict,
        )
        # TODO: add new random option setting
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

    recipe_in = schemas.RecipeUpdate(name=body.name)
    recipe = await crud.recipe.update(
        db_session=db_session,
        obj_current=recipe,
        obj_new=recipe_in,
        autocommit=False,
    )

    parameters_input = body.analytical_params
    # TODO: validate params
    owner_id = "24a8dd68-f304-4eb6-b7ed-c6978943d090"
    recipe_parameter_in_list = []
    parameters_dict = parameters_input.dict(exclude_none=True)
    for key, value in parameters_dict.items():
        # TODO: check key and value valid
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
    db_session.commit()

    # TODO: handle charts info

    recipe_in = schemas.RecipeUpdate(stage="analytical", is_active=True)
    recipe = await crud.recipe.update(
        db_session=db_session,
        obj_current=recipe,
        obj_new=recipe_in,
    )

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
        raise HTTPException(404, f"Recipe {recipe_id} not found")

    # TODO: validate params
    error_dict = await validate_values(
        db_session=db_session,
        parameters_input=parameters_input,
    )
    if error_dict:
        raise HTTPException(422, detail=json.dumps(error_dict))

    # TODO: calculate analytical result
    mock_data = get_mock_chart_data()
    return schemas.RecipeWithChartsResponse(recipe=recipe, charts=mock_data["chart"])
