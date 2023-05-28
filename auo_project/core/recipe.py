import json
import re
from datetime import datetime
from typing import List

import pydash as py_
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud
from auo_project.core.constants import ParameterType

disease_value_pattern = re.compile(r"^d[0-9]{3}:[0-9]{3}$")


def is_valid_month(dt_str):
    try:
        datetime.strptime(dt_str, "%Y-%m")
        return True
    except ValueError:
        return False


def is_valid_date(dt_str):
    try:
        datetime.strptime(dt_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_hour(dt_str):
    try:
        datetime.strptime(dt_str, "%H:%M")
        return True
    except ValueError:
        return False


def handle_date_related_params(loaded_value, component_names):
    unit = loaded_value.get("unit")
    # calendar_date
    if unit == "day" and "start" in loaded_value and "end" in loaded_value:
        if "calendar_date" not in component_names:
            raise ValueError(
                "the value is belong to calendar_date but there is no component in it",
            )
        start = loaded_value["start"]
        end = loaded_value["end"]
        if not (is_valid_date(start) and is_valid_date(end)):
            raise ValueError(
                f"start: {start} or end: {end} is not valid date format (YYYY-MM-DD)",
            )
        elif start > end:
            raise ValueError(f"start: {start} is greater than end: {end}")
        return json.dumps(loaded_value), ""

    # measure_date_or_month
    if unit in ("day", "month") and "values" in loaded_value:
        values = loaded_value.get("values")
        if "measure_date_or_month" not in component_names:
            raise ValueError(
                "the value is belong to measure_date_or_month but there is no component in it",
            )
        if unit == "day":
            if not all([is_valid_date(value) for value in values]):
                raise ValueError(
                    f"values: {values} is not valid date format (YYYY-MM-DD)",
                )
            # TODO: check duplicates rows
            return json.dumps(loaded_value), ""
        elif unit == "month":
            if not all([is_valid_month(value) for value in values]):
                raise ValueError(
                    f"values: {values} is not valid month format (YYYY-MM)",
                )
            # TODO: check duplicates rows
            return json.dumps(loaded_value), ""

    # hour
    if unit == "hour" and "start" in loaded_value and "end" in loaded_value:
        if "calendar_date" not in component_names:
            raise ValueError(
                "the value is belong to hour but there is no component in it",
            )
        start = loaded_value["start"]
        end = loaded_value["end"]
        if not (is_valid_hour(start) and is_valid_hour(end)):
            raise ValueError(f"{start} or {end} is not valid hour format (HH:MM)")
        elif start > end:
            raise ValueError(f"start: {start} is greater than end: {end}")
        return json.dumps(loaded_value), ""


# TODO: send path to func
def deep_search(field, component_names, value, result_list=[]):
    if field.get("type") == "group":
        for field in field["subField"]:
            result_list += deep_search(field, component_names, value, [])
    else:
        options = py_.get(field, "subField.options", [])
        for option in options:
            result_list += deep_search(option, component_names, value, [])
        else:
            if isinstance(value, str):
                if field.get("value") == value:
                    result_list.append(
                        {"value": field["value"], "path": f"subField.options"},
                    )
            elif isinstance(value, list):
                if field.get("value") in value:
                    result_list.append(
                        {"value": field["value"], "path": f"subField.options"},
                    )

    return result_list


def find_all_component_names(parameter) -> List[str]:
    component_names = []
    if parameter.get("type") == "group":
        for field in parameter["subField"]:
            component_names += find_all_component_names(field)
    else:
        subField = parameter.get("subField")
        if not subField:
            return component_names

        component_names.append(subField.get("component"))
        options = subField.get("options", [])
        for option in options:
            if option.get("subField"):
                component_names += find_all_component_names(option)
    component_names = list(set([name for name in component_names if name]))
    return component_names


async def validate_value(
    parameter_id: str,
    value: str,
    parameter_options_dict: dict,
    disease_options_dict: dict,
):
    parameter = parameter_options_dict.get(parameter_id)
    if not parameter:
        raise ValueError(f"the parameter id {parameter_id} is not found")
    if parameter.get("type") == "group":
        raise ValueError("the input parameter should not be group")

    component_names = find_all_component_names(parameter)

    loaded_value = value
    try:
        loaded_value = json.loads(value)
    except:
        pass

    # 單一比對疾病, 交叉比對疾病
    if parameter_id == "a008":
        return handle_disease_params(loaded_value, disease_options_dict)
    # 比較單一脈象, 交叉比對脈象
    elif parameter_id == "a027":
        return handle_pulse_condition_params(loaded_value)

    # 每一個問題都有 all
    if value == "all":
        return value, "subField.options"
    # value 不可以是 custom，應該是 custom 底下 options 的 value
    if value == "custom":
        raise ValueError("value cannot be custom")

    # 若 value 是一個字串，應該是 radio 或 dropdown 的 value
    p = re.compile(r"^c[0-9]{3}:[0-9]{3}$")
    if isinstance(loaded_value, str) and p.search(loaded_value):
        result_list = deep_search(parameter, ["radio", "dropdown"], loaded_value, [])
        if len(result_list) == 0:
            raise ValueError(f"the value {value} is not found")
        elif len(result_list) > 1:
            raise ValueError(f"the value {value} is not unique")
        return str(result_list[0]["value"]), ""

    # 若 value 是一個 list，應該是 checkbox 的 value，如果是 checkbox 的 option 底下的 value，應該符合 c001:000 的格式
    multi_choices_components_set = set(
        ["checkbox", "search_dialog", "multi_select_dialog"],
    )
    if multi_choices_components_set & set(component_names):
        if isinstance(loaded_value, list) and all(
            [p.search(value) for value in loaded_value],
        ):
            result_list = deep_search(parameter, ["checkbox"], loaded_value, [])
            if len(result_list) == 0:
                raise ValueError(f"the value {value} is not found")
            elif len(result_list) != len(loaded_value):
                result_value_list = [result["value"] for result in result_list]
                diff_str = ",".join(
                    set(loaded_value).difference(set(result_value_list)),
                )
                raise ValueError(f"some value is not found: {diff_str}")
            return value, "subField.options"
        elif isinstance(loaded_value, list):
            result_list = deep_search(
                parameter,
                ["checkbox", "search_dialog", "multi_select_dialog"],
                loaded_value,
                [],
            )
            if len(result_list) != len(loaded_value):
                raise ValueError(
                    f"some elements of {value} are not align with option values",
                )
            return value, "subField.options"

    # 若為 dict 且存在 key: unit 則為 date-related 的 value。而參數對應的 component 可能為 measure_date_or_month, calendar_date
    if isinstance(loaded_value, dict) and loaded_value.get("unit"):
        return handle_date_related_params(loaded_value, component_names)

    # 若上面都找不到，可能為 input
    if "input" in component_names:
        if isinstance(loaded_value, int):
            # TODO: check valid range
            return str(loaded_value), "subField"

    raise ValueError(f"the value {value} is not found")


def handle_disease_single_params(loaded_value, disease_options_dict):
    disease_value_pattern = re.compile(r"^d[0-9]{3}:[0-9]{3}$")
    if all([isinstance(e, str) for e in loaded_value]):
        if not all([disease_value_pattern.search(e) for e in loaded_value]):
            invalid_values = [
                e for e in loaded_value if not disease_value_pattern.search(e)
            ]
            raise ValueError(
                f"values: {invalid_values} are not belong to disease options",
            )
        elif not all([e in disease_options_dict for e in loaded_value]):
            invalid_values = [e for e in loaded_value if e not in disease_options_dict]
            raise ValueError(
                f"values: {invalid_values} are not belong to disease options",
            )
        else:
            return loaded_value, "subField.options"


def handle_disease_cross_params(loaded_value, disease_options_dict):
    if len(loaded_value) > 5:
        raise ValueError("cross disease params should be less than 6")

    disease_value_pattern = re.compile(r"^d[0-9]{3}:[0-9]{3}$")
    for e in loaded_value:
        if not ("include" in e and "exclude" in e):
            raise ValueError(
                "cross disease params value should be all has include and exclude key",
            )
        all_include = e["include"]
        if len(all_include) != 1:
            raise ValueError("include disease only accpets one value")
        if not all([disease_value_pattern.search(e) for e in all_include]):
            invalid_values = [
                e for e in all_include if not disease_value_pattern.search(e)
            ]
            raise ValueError(
                f"values: {invalid_values} are not belong to disease options",
            )
        elif not all([e in disease_options_dict for e in all_include]):
            invalid_values = [e for e in all_include if e not in disease_options_dict]
            raise ValueError(
                f"values: {invalid_values} are not belong to disease options",
            )
        all_exclude = e["exclude"]
        # TODO: check max exclude option number
        if not all([disease_value_pattern.search(e) for e in all_exclude]):
            invalid_values = [
                e for e in all_exclude if not disease_value_pattern.search(e)
            ]
            raise ValueError(
                f"values: {invalid_values} are not belong to disease options",
            )
        elif not all([e in disease_options_dict for e in all_exclude]):
            invalid_values = [e for e in all_exclude if e not in disease_options_dict]
            raise ValueError(
                f"values: {invalid_values} are not belong to disease options",
            )
    return loaded_value, "subField.options"


def handle_disease_params(loaded_value, disease_options_dict):
    if loaded_value == "all":
        return loaded_value, ""
    if isinstance(loaded_value, list):
        if len(loaded_value) == 0:
            raise ValueError("disease params should not be empty")
        # single disease
        if all([isinstance(e, str) for e in loaded_value]):
            result, path = handle_disease_single_params(
                loaded_value,
                disease_options_dict,
            )
            if result and path:
                return json.dumps(result), path
        # cross disease
        else:
            result, path = handle_disease_cross_params(
                loaded_value,
                disease_options_dict,
            )
            if result and path:
                return json.dumps(result), path

    raise ValueError("disease params should be list of string or list of dictionay")


def handle_pulse_condition_params(loaded_value):
    return loaded_value, ""


def process_option_component(x):
    other_constraint = {}
    if not x:
        return None, other_constraint
    if "|" in x:
        s = x.split("|")
        real_component = s[0]
        other_constraint_rules = s[1:]
        for rule in other_constraint_rules:
            key = rule.split(":")[0]
            value = rule.split(":")[1]
            other_constraint[key] = value
        return real_component, other_constraint
    return x, {}


def find_childs(
    output_result,
    parameter,
    to_delete,
    parent_childs,
    output_result_paramter_id_idx,
):
    child_ids = []
    if hasattr(parameter, "has_childs") and getattr(parameter, "has_childs"):
        child_ids = parent_childs[parameter.id]
        to_delete += child_ids
        output_result[parameter.p_type][
            output_result_paramter_id_idx[parameter.p_type][parameter.id]
        ]["type"] = "group"
        output_result[parameter.p_type][
            output_result_paramter_id_idx[parameter.p_type][parameter.id]
        ]["subField"] = []
        for child_id in child_ids:
            if child_id in output_result_paramter_id_idx[parameter.p_type]:
                # print(f"child id {child_id} correct")
                pass
            idx = output_result_paramter_id_idx[parameter.p_type][child_id]
            try:
                child = output_result[parameter.p_type][idx]
                to_delete += find_childs(
                    output_result,
                    child,
                    to_delete,
                    parent_childs,
                    output_result_paramter_id_idx,
                )
                output_result[parameter.p_type][
                    output_result_paramter_id_idx[parameter.p_type][parameter.id]
                ]["subField"].append(child)
            except Exception as e:
                print(f"idx {idx} error", e)
                print(
                    "output_result[parameter.p_type]",
                    output_result[parameter.p_type],
                )
    return child_ids


async def process_child_parents(
    parameters,
    question_options_dict,
    parameter_options_dict,
    allowed_p_types,
):

    output_result = {"primary": [], "secondary": [], "analytical": []}

    parameter_dict = {}
    output_result_paramter_id_idx = {}
    parent_childs = {}
    for parameter in parameters:
        parameter_dict[parameter.id] = parameter
    for parameter in parameters:
        if parameter.parent_id:
            parent_childs.setdefault(parameter.parent_id, [])
            parent_childs[parameter.parent_id].append(parameter.id)

    idx1 = 0
    idx2 = 0
    idx3 = 0
    for idx in range(len(parameters)):
        parameter = parameters[idx]
        output_result_paramter_id_idx.setdefault(parameter.p_type, {})
        if parameter.option_category_id in question_options_dict:
            real_component, other_constraint = process_option_component(
                parameter.option_component,
            )

            output_result[parameter.p_type].append(
                {
                    "id": parameter.id,
                    "label": parameter.label,
                    "subField": {
                        **other_constraint,
                        "type": parameter.option_type,
                        "component": real_component,
                        "options": question_options_dict[parameter.option_category_id],
                    },
                },
            )

        elif parameter.id in parameter_options_dict:
            real_component, other_constraint = process_option_component(
                parameter.option_component,
            )
            output_result[parameter.p_type].append(
                {
                    "id": parameter.id,
                    "label": parameter.label,
                    "subField": {
                        **other_constraint,
                        "type": parameter.option_type,
                        "component": real_component,
                        "options": parameter_options_dict[parameter.id],
                    },
                },
            )

        elif parameter.has_childs:
            output_result[parameter.p_type].append(
                {"id": parameter.id, "label": parameter.label, "type": "group"},
            )
        else:
            raise Exception(f"not found related info: {parameter}")

        if parameter.p_type == "primary":
            output_result_paramter_id_idx[parameter.p_type][parameter.id] = idx1
            idx1 += 1
        elif parameter.p_type == "secondary":
            output_result_paramter_id_idx[parameter.p_type][parameter.id] = idx2
            idx2 += 1
        elif parameter.p_type == "analytical":
            output_result_paramter_id_idx[parameter.p_type][parameter.id] = idx3
            idx3 += 1

    to_delete = []
    for parameter in parameters:
        to_delete += find_childs(
            output_result,
            parameter,
            to_delete,
            parent_childs,
            output_result_paramter_id_idx,
        )

    new_output_result = {}
    for p_type in allowed_p_types:
        new_output_result[p_type] = []
        for x in output_result.get(p_type, []):
            if not x["id"] in to_delete:
                new_output_result[p_type].append(x)
    return new_output_result


async def process_child_parents2(
    parameters,
    question_options_dict,
    parameter_options_dict,
    allowed_p_types,
):

    output_result_dict = {}

    parameter_dict = {}
    output_result_paramter_id_idx = {}
    parent_childs = {}
    for parameter in parameters:
        parameter_dict[parameter.id] = parameter
    for parameter in parameters:
        if parameter.parent_id:
            parent_childs.setdefault(parameter.parent_id, [])
            parent_childs[parameter.parent_id].append(parameter.id)

    for idx in range(len(parameters)):
        parameter = parameters[idx]
        output_result_paramter_id_idx.setdefault(parameter.p_type, {})
        if parameter.option_category_id in question_options_dict:
            real_component, other_constraint = process_option_component(
                parameter.option_component,
            )
            output_result_dict[parameter.id] = {
                "id": parameter.id,
                "label": parameter.label,
                "subField": {
                    **other_constraint,
                    "type": parameter.option_type,
                    "component": real_component,
                    "options": question_options_dict[parameter.option_category_id],
                },
            }

        elif parameter.id in parameter_options_dict:
            real_component, other_constraint = process_option_component(
                parameter.option_component,
            )
            output_result_dict[parameter.id] = {
                "id": parameter.id,
                "label": parameter.label,
                "subField": {
                    **other_constraint,
                    "type": parameter.option_type,
                    "component": real_component,
                    "options": parameter_options_dict[parameter.id],
                },
            }

        elif parameter.has_childs:
            output_result_dict[parameter.id] = {
                "id": parameter.id,
                "label": parameter.label,
                "type": "group",
            }
        else:
            raise Exception(f"not found related info: {parameter}")

    return output_result_dict


def get_time_related_parameters(parameter_options_dict):
    time_related_parameters = []
    for parameter_id, options in parameter_options_dict.items():
        print(options)
        time_components = set(["calendar_date", "measure_date_or_month"])
        for option in options:
            if option.get("component") in time_components:
                time_related_parameters.append(parameter_id)
            elif py_.get(option, "subField.component") in time_components:
                time_related_parameters.append(parameter_id)
            else:
                child_options = py_.get(option, "subField.options", [])
                for child_option in child_options:
                    if child_option.get("component") in time_components:
                        time_related_parameters.append(parameter_id)
    return time_related_parameters


def get_time_related_parameters_dict(parameter_options_dict):
    time_related_parameters_dict = {}
    for parameter_id, options in parameter_options_dict.items():
        print(options)
        time_components = set(["calendar_date", "measure_date_or_month"])
        for option in options:
            if option.get("component") in time_components:
                time_related_parameters_dict[parameter_id].setdefault([])
                time_related_parameters_dict[parameter_id].append(
                    option.get("component"),
                )
            elif py_.get(option, "subField.component") in time_components:
                time_related_parameters_dict[parameter_id].setdefault([])
                time_related_parameters_dict[parameter_id].append(
                    py_.get(option, "subField.component"),
                )
            else:
                child_options = py_.get(option, "subField.options", [])
                for child_option in child_options:
                    if child_option.get("component") in time_components:
                        time_related_parameters_dict[parameter_id].setdefault([])
                        time_related_parameters_dict[parameter_id].append(
                            child_option.get("component"),
                        )
    return time_related_parameters_dict


async def get_parameters(
    db_session: AsyncSession,
    p_types: List[ParameterType],
    process_child_parent: bool = True,
):
    if not all([isinstance(e, ParameterType) for e in p_types]):
        raise HTTPException(
            status_code=400,
            detail="p_types must be a list of ParameterType",
        )

    parameter_options_dict = {}
    parameters = await crud.measure_parameter.get_all(db_session=db_session)
    allowed_p_types = set([p_type.value for p_type in p_types])
    parameters = [e for e in parameters if e.p_type in allowed_p_types]
    parameters_dict = dict([(parameter.id, parameter) for parameter in parameters])

    parameter_options = await crud.measure_parameter_option.get_all(
        db_session=db_session,
    )
    question_options = await crud.measure_question_option.get_all(db_session=db_session)

    question_options_dict = {}
    for option in question_options:
        question_options_dict.setdefault(option.category_id, [])
        if "column:infos.proj_num" == option.value:
            values = await crud.measure_info.get_proj_num(db_session=db_session)
            question_options_dict[option.category_id] = values
        elif "column:infos.cusult_dr" == option.value:
            values = await crud.measure_info.get_consult_dr(db_session=db_session)
            question_options_dict[option.category_id] = values
        elif "column:auth_orgs.name" == option.value:
            values = await crud.measure_info.get_org_name(db_session=db_session)
            question_options_dict[option.category_id] = values
        elif "column:infos.measure_operator" == option.value:
            values = await crud.measure_info.get_measure_operator(db_session=db_session)
            question_options_dict[option.category_id] = values
        else:
            real_component, other_constraint = process_option_component(
                option.component,
            )
            new_option = {
                "value": f"{option.category_id}:{option.value}",
                "label": option.label,
                "component": real_component,
            }
            if other_constraint:
                new_option["subField"] = {
                    **other_constraint,
                    "component": real_component,
                }
                del new_option["component"]

            if "component" in new_option and not new_option["component"]:
                del new_option["component"]
            question_options_dict[option.category_id].append(new_option)

    for option in parameter_options:
        real_component, other_constraint = process_option_component(
            option.option_component,
        )
        parameter_options_dict.setdefault(option.parent_id, [])
        new_option = {
            "value": option.value,
            "label": option.label,
        }
        parent_parameter = parameters_dict.get(option.parent_id)
        if option.option_type:
            new_option["subField"] = {
                **other_constraint,
                "type": option.option_type,
                "component": real_component,
                "postfix": option.label_suffix,
            }
            if not new_option["subField"]["postfix"]:
                del new_option["subField"]["postfix"]
            if option.option_category_id in question_options_dict:
                new_option["subField"]["options"] = question_options_dict[
                    option.option_category_id
                ]
            elif option.value in ("disease_single", "disease_cross"):
                transformed = (
                    await crud.measure_disease_option.get_disease_level_options(
                        db_session=db_session,
                    )
                )
                # values = await crud.measure_disease_option.get_all(
                #     db_session=db_session
                # )
                # transformed = (
                #     py_.chain(values)
                #     .group_by("category_id")
                #     .map_(
                #         lambda value: {
                #             "category_id": value[0].category_id,
                #             "category_name": value[0].category_name,
                #             "diseases": [
                #                 {
                #                     "value": f"{value[0].category_id}:{e.value}",
                #                     "label": e.label,
                #                 }
                #                 for e in value
                #             ],
                #         }
                #     )
                #     .value()
                # )
                new_option["subField"]["options"] = transformed

            # add title
            if "dialog" in option.option_component:
                if parent_parameter:
                    new_option["subField"]["title"] = f"選擇{parent_parameter.label}"

            if "measure_date_or_month" == option.option_component:
                if parent_parameter:
                    new_option["subField"]["title"] = parent_parameter.label

        parameter_options_dict[option.parent_id].append(new_option)

    if process_child_parent:
        new_output_result = await process_child_parents(
            parameters,
            question_options_dict,
            parameter_options_dict,
            allowed_p_types,
        )
        return new_output_result
    else:
        output_result = await process_child_parents2(
            parameters,
            question_options_dict,
            parameter_options_dict,
            allowed_p_types,
        )
        return output_result


def add_default_value_to_parameter(parameter):
    for field in parameter:
        if field.get("type") == "group":
            add_default_value_to_parameter(field["subField"])
        else:
            options = field.get("subField", {}).get("options", [])
            if options and len(options) > 0:
                field["defaultValue"] = options[0]["value"]
                field["path"] = "subField.options.0.value"
                print(field["subField"]["component"])
                if field["subField"]["component"] in ("radio", "checkbox"):
                    field["subField"]["options"][0] = {
                        **field["subField"]["options"][0],
                        "selected": True,
                    }
    return parameter


def handle_all():
    pass


def handle_radio():
    pass


def handle_input():
    pass


def handle_string():
    handle_all()
    handle_radio()
    handle_input()


def handle_simple_list():
    pass


def handle_list_of_list():
    pass


def handle_list_of_dict():
    pass


def add_selected_key(field, value):
    options = field.get("subField", {}).get("options", [])
    if options and len(options) > 0:
        if field["subField"]["component"] in ("radio", "checkbox"):
            for option in options:
                if option["value"] == value:
                    option["selected"] = True
    return field


def add_recipe_value_to_parameter(parameter, recipe_params_dict):
    for field in parameter:
        parameter_id = field.get("id")
        recipe_param = recipe_params_dict.get(parameter_id)
        if not recipe_param:
            continue
        if field.get("type") == "group":
            add_recipe_value_to_parameter(field["subField"], recipe_params_dict)
        else:
            field["defaultValue"] = recipe_param.value
            # TODO: add path
            field = add_selected_key(field, recipe_param.value)
    return parameter
