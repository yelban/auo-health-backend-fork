import json
import re
from datetime import datetime
from typing import List

import pydash as py_
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from auo_project import crud, schemas
from auo_project.core.constants import AdvanceChartType, ParameterType

disease_value_pattern = re.compile(r"^d[0-9]{3}:[0-9]{3}$")


def clean_last_pattern(s, pattern):
    if s.rfind(pattern) != -1:
        return s[: s.rfind(pattern)] + "subField"
    else:
        return s


def is_valid_month(dt_str):
    try:
        if "-" in dt_str:
            datetime.strptime(dt_str, "%Y-%m")
        elif "/" in dt_str:
            datetime.strptime(dt_str, "%Y/%m")
        return True
    except ValueError:
        return False


def is_valid_date(dt_str):
    try:
        if "-" in dt_str:
            datetime.strptime(dt_str, "%Y-%m-%d")
        elif "/" in dt_str:
            datetime.strptime(dt_str, "%Y/%m/%d")
        return True
    except ValueError:
        return False


def is_valid_hour(dt_str):
    try:
        datetime.strptime(dt_str, "%H:%M")
        return True
    except ValueError:
        return False


def get_loaded_value(value):
    loaded_value = value
    try:
        loaded_value = json.loads(value)
    except:
        pass
    return loaded_value


def handle_simple_dt_list(loaded_value):
    if all([is_valid_date(e) for e in loaded_value]):
        return json.dumps(loaded_value), "measure_date_or_month"
    elif all([is_valid_month(e) for e in loaded_value]):
        return json.dumps(loaded_value), "measure_date_or_month"
    else:
        raise ValueError("the value is not valid date or month format")


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
        return json.dumps(loaded_value), "calendar_date"

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
            return json.dumps(loaded_value), "measure_date_or_month"
        elif unit == "month":
            if not all([is_valid_month(value) for value in values]):
                raise ValueError(
                    f"values: {values} is not valid month format (YYYY-MM)",
                )
            # TODO: check duplicates rows
            return json.dumps(loaded_value), "measure_date_or_month"

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
        return json.dumps(loaded_value), "calendar_date"


def deep_search(
    field,
    component_names,
    value,
    result_list=[],
    path="",
    parent_component=None,
):
    if field.get("type") == "group":
        for field in field["subField"]:
            result_list += deep_search(
                field,
                component_names,
                value,
                [],
                f"{path}.subField",
                None,
            )
    else:
        options = py_.get(field, "subField.options", [])
        for idx, option in enumerate(options):
            result_list += deep_search(
                option,
                component_names,
                value,
                [],
                f"{path}.subField.options.{idx}",
                py_.get(field, "subField.component"),
            )
        else:
            if parent_component in component_names:
                if isinstance(value, str):
                    if field.get("value") == value:
                        result_list.append(
                            {
                                "value": field["value"],
                                "path": f"{path}",
                                "component": parent_component,
                            },
                        )
                elif isinstance(value, list):
                    if field.get("value") in value:
                        result_list.append(
                            {
                                "value": field["value"],
                                "path": f"{path}",
                                "component": parent_component,
                            },
                        )

    return result_list


def find_component_path(field, component_name, result_list=[], path="") -> List[str]:
    if field.get("type") == "group":
        for field in field["subField"]:
            result_list += deep_search(field, component_name, [], f"{path}.subField")
    else:
        if component_name == field.get("subField.component"):
            result_list.append(f"{path}.subField.component")
        options = py_.get(field, "subField.options", [])
        for idx, option in enumerate(options):
            result_list += find_component_path(
                option,
                component_name,
                [],
                f"{path}.subField.options.{idx}",
            )
        else:
            if py_.get(field, "subField.component") == component_name:
                result_list.append(f"{path}.subField.component")
    return result_list


def find_all_component_names(parameter) -> List[str]:
    component_names = []
    if parameter.get("type") == "group" and parameter.get("subField"):
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

    loaded_value = get_loaded_value(value)

    # 不是每一個問題都有 all，不允許 all 的：a003, a025, a032
    # TODO: refactor
    if value == "all" and parameter_id in ("a003", "a025", "a032"):
        raise ValueError(f"the value {value} is not found")
    if value == "all":
        return value, {"path": ".subField.options.0", "component": "radio"}

    # value 不可以是 custom，應該是 custom 底下 options 的 value
    if value == "custom":
        raise ValueError("value cannot be custom")

    # TODO: add date or month
    # if parameter_id == "a001":
    #     component_paths = find_component_path(parameter, "measure_date_or_month", [])
    #     if len(component_paths) != 1:
    #         raise ValueError(f"component_paths length should be 1")
    #     value, component = handle_simple_dt_list(loaded_value)
    #     return value, {
    #         "path": component_paths[0].replace(".component", ""),
    #         "component": component,
    #     }

    # 單一比對疾病, 交叉比對疾病
    if parameter_id == "a008":
        value, component = handle_disease_params(loaded_value, disease_options_dict)
        component_paths = find_component_path(parameter, component, [])
        if len(component_paths) != 1:
            raise ValueError(f"component_paths length should be 1")
        return value, {
            "path": component_paths[0].replace(".component", ""),
            "component": component,
        }
    # 比較單一脈象, 交叉比對脈象
    elif parameter_id == "a027":
        pulse_condition_options = py_.get(
            parameter_options_dict,
            f"{parameter_id}.subField.options.1.subField.options",
        )
        pulse_condition_options_dict = {
            option["value"]: option for option in pulse_condition_options
        }
        value, component = handle_pulse_condition_params(
            loaded_value,
            pulse_condition_options_dict,
        )
        component_paths = find_component_path(parameter, component, [])
        if len(component_paths) != 1:
            raise ValueError(f"component_paths length should be 1")
        return value, {"path": component_paths[0], "component": component}

    # 若 value 是一個字串，應該是 radio 或 dropdown 的 value
    p = re.compile(r"^c[0-9]{3}:[0-9]{3}$")
    if isinstance(loaded_value, str) and p.search(loaded_value):
        result_list = deep_search(parameter, ["radio", "dropdown"], loaded_value, [])
        if len(result_list) == 0:
            raise ValueError(f"the value {value} is not found")
        elif len(result_list) > 1:
            raise ValueError(f"the value {value} is not unique")
        return str(result_list[0]["value"]), {
            "path": result_list[0]["path"],
            "component": result_list[0]["component"],
        }

    # 若 value 是一個 list，應該是 checkbox 的 value，如果是 checkbox 的 option 底下的 value，應該符合 c001:000 的格式
    multi_choices_components_set = set(
        ["checkbox", "search_dialog", "multi_select_dialog"],
    )
    if multi_choices_components_set & set(component_names):
        if isinstance(loaded_value, list) and all(
            [p.search(value) for value in loaded_value],
        ):
            result_list = deep_search(
                parameter,
                ["checkbox", "search_dialog", "multi_select_dialog"],
                loaded_value,
                [],
            )
            if len(result_list) == 0:
                raise ValueError(f"the value {value} is not found")
            elif len(result_list) != len(loaded_value):
                result_value_list = [result["value"] for result in result_list]
                diff_str = ",".join(
                    set(loaded_value).difference(set(result_value_list)),
                )
                raise ValueError(f"some value is not found: {diff_str}")
            return value, {
                "path": [result["path"] for result in result_list],
                "component": [result["component"] for result in result_list],
            }
        # special options from database
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
            return value, {
                "path": [result["path"] for result in result_list],
                "component": [result["component"] for result in result_list],
            }

    # 若為 dict 且存在 key: unit 則為 date-related 的 value。而參數對應的 component 可能為 measure_date_or_month, calendar_date
    if isinstance(loaded_value, dict) and loaded_value.get("unit"):
        value, component = handle_date_related_params(loaded_value, component_names)
        component_paths = find_component_path(parameter, component, [])
        if len(component_paths) != 1:
            raise ValueError(f"component_paths length should be 1")
        return value, {
            "path": component_paths[0].replace(".component", ""),
            "component": component,
        }

    # 若上面都找不到，可能為 input
    if "input" in component_names:
        if isinstance(loaded_value, int):
            # TODO: check valid range
            component_paths = find_component_path(parameter, "input", [])
            if len(component_paths) != 1:
                raise ValueError(f"component_paths length should be 1")
            return str(loaded_value), {
                "path": component_paths[0].replace(".component", ""),
                "component": "input",
            }

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
            return loaded_value


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
    return loaded_value


def handle_disease_params(loaded_value, disease_options_dict):
    if loaded_value == "all":
        return loaded_value, ""
    if isinstance(loaded_value, list):
        if len(loaded_value) == 0:
            raise ValueError("disease params should not be empty")
        # single disease
        if all([isinstance(e, str) for e in loaded_value]):
            result = handle_disease_single_params(
                loaded_value,
                disease_options_dict,
            )
            if result:
                return json.dumps(result), "multi_select_dialog_disease_single"
        # cross disease
        else:
            result = handle_disease_cross_params(
                loaded_value,
                disease_options_dict,
            )
            if result:
                return json.dumps(result), "multi_select_dialog_disease_cross"

    raise ValueError("disease params should be list of string or list of dictionay")


def handle_pulse_condition_params(loaded_value, pulse_condition_options_dict):
    if all([isinstance(option, str) for option in loaded_value]):
        invalid_values = [
            e for e in loaded_value if e not in pulse_condition_options_dict
        ]
        if len(invalid_values) > 0:
            raise ValueError(
                f"values: {invalid_values} are not belong to disease options",
            )
        return json.dumps(loaded_value), "multi_select_dialog_pulse_condition_single"

    if all([isinstance(option, list) for option in loaded_value]):
        if len(loaded_value) == 0:
            raise ValueError(
                "cross pulse condition params length should be more than 0",
            )
        elif len(loaded_value) > 3:
            raise ValueError(
                "cross pulse condition params length should be less than 4",
            )
        for option in loaded_value:
            result, component = handle_pulse_condition_params(
                option,
                pulse_condition_options_dict,
            )
            if (
                result == json.dumps(option)
                and component == "multi_select_dialog_pulse_condition_single"
            ):
                continue
            else:
                raise ValueError(f"something error: {option}")
        return json.dumps(loaded_value), "multi_select_dialog_pulse_condition_cross"
    raise ValueError(
        "pulse condition params should be list of string or list of list of string",
    )


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
                    # "hide_label": parameter.hide_label,
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
                    "hide_label": parameter.hide_label,
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
    parameters = sorted(
        [e for e in parameters if e.p_type in allowed_p_types],
        key=lambda e: e.id,
    )
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
        if field.get("type") == "group":
            if field.get("subField"):
                add_recipe_value_to_parameter(field.get("subField"), recipe_params_dict)
            continue

        parameter_id = field.get("id")
        recipe_param = recipe_params_dict.get(parameter_id)
        if not recipe_param:
            continue

        else:
            field["defaultValue"] = recipe_param.value
            # TODO: add path
            field = add_selected_key(field, recipe_param.value)
    return parameter


def parse_subfield_options_old(field_path):
    paths = field_path.split(".subField.options.")
    result = []

    for i in range(len(paths)):
        test = ".subField.options.".join(paths[:i]) + ".subField.defaultValue"
        value = ".subField.options.".join(paths[: i + 1])
        if value == "":
            continue
        if i < len(paths) - 1:
            result.append((test, f"{value}.value"))
        else:
            result.append((test, f"{value}.value"))

    return result


def parse_subfield_options(field_path):
    paths = field_path.split(".subField")
    result = []

    for i in range(len(paths)):
        test = ".subField".join(paths[:i]) + ".subField.defaultValue"
        value = ".subField".join(paths[: i + 1])
        if value == "":
            continue
        if i < len(paths) - 1:
            result.append((test, f"{value}.value"))
        else:
            result.append((test, f"{value}.value"))

    return result


def handle_default_value(parameter, info):
    path = info["path"]
    if isinstance(path, str):
        parsed_paths = parse_subfield_options(path)
        # set deepest value
        py_.set_(parameter, parsed_paths[-1][0], info["result"])
        # set upper level value
        for dest_path, source_path in parsed_paths[:-1]:
            py_.set_(parameter, dest_path, py_.get(parameter, source_path))
    elif isinstance(path, list):
        # take first path and its level should be the same
        parsed_paths = parse_subfield_options(path[0])
        # set deepest value
        py_.set_(parameter, parsed_paths[-1][0], info["result"])
        # set upper level value
        parsed_paths = parsed_paths[:-1]
        for dest_path, source_path in parsed_paths:
            py_.set_(parameter, dest_path, py_.get(parameter, source_path))

    else:
        raise TypeError("path type error")

    return parameter


def add_parameter_internal_value(parameter, infos_dict):
    info_dict = infos_dict.get(parameter["id"])
    if parameter.get("type") != "group":
        handle_default_value(parameter, info_dict)
        path = info_dict["path"]
        if isinstance(path, str):
            parameter["path"] = clean_last_pattern(path, "subField")
        elif isinstance(path, list):
            parameter["path"] = clean_last_pattern(path[0], "subField")
        else:
            raise ValueError("path type error")

    else:
        for sub_parameter in parameter.get("subField"):
            add_parameter_internal_value(sub_parameter, infos_dict)


def get_default_chart_settings():
    default_chart_settings = [
        {
            "chart_type": AdvanceChartType.parameter_six_pulse,
            "y": {"domain": ["time_domain", "h1"]},
            "z": "a004",
        },
        {
            "chart_type": AdvanceChartType.parameter_cross,
            "x": "a007",
            "y": {"six_pulse": "l_cu", "domain": ["time_domain", "h1"]},
            "z": "a004",
        },
        {
            "chart_type": AdvanceChartType.six_pulse_cn,
            "y": {"six_pulse": "l_cu", "statistics": "mean"},
            "z": "a004",
        },
    ]
    return default_chart_settings


def validate_chart_setting(chart_setting: schemas.ChartSetting):
    if chart_setting.chart_type == AdvanceChartType.parameter_six_pulse:
        domain = chart_setting.y.get("domain")
        if not (domain and isinstance(domain, list)):
            raise HTTPException(
                status_code=400,
                detail=f"chart_type {chart_setting.chart_type} input y error",
            )
    elif chart_setting.chart_type == AdvanceChartType.parameter_cross:
        domain = chart_setting.y.get("domain")
        if not (domain and isinstance(domain, list)):
            raise HTTPException(
                status_code=400,
                detail=f"chart_type {chart_setting.chart_type} input y error",
            )
        six_pulse = chart_setting.y.get("six_pulse")
        if not isinstance(six_pulse, str):
            raise HTTPException(
                status_code=400,
                detail=f"chart_type {chart_setting.chart_type} input y error",
            )

        if not chart_setting.x:
            raise HTTPException(
                status_code=400,
                detail=f"chart_type {chart_setting.chart_type} need x",
            )

    elif chart_setting.chart_type == AdvanceChartType.six_pulse_cn:
        six_pulse = chart_setting.y.get("six_pulse")
        if not isinstance(six_pulse, str):
            raise HTTPException(
                status_code=400,
                detail=f"chart_type {chart_setting.chart_type} input y error",
            )
        statistics = chart_setting.y.get("statistics")
        if statistics not in ("mean", "std", "cv"):
            raise HTTPException(
                status_code=400,
                detail=f"chart_type {chart_setting.chart_type} input y error",
            )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"chart_type {chart_setting.chart_type} not found",
        )


def get_flat_parameter_dict(parameters):
    """
    {"primary": [], "secondary": [], "analytical": []}
    """
    parameter_list = []
    if isinstance(parameters, dict):
        if "primary" in parameters:
            parameter_list += parameters["primary"]
        if "secondary" in parameters:
            parameter_list += parameters["secondary"]
        if "analytical" in parameters:
            parameter_list += parameters["analytical"]
    elif isinstance(parameters, list):
        parameter_list = parameters

    result = {}
    for parameter in parameter_list:
        if parameter.get("type") == "group":
            result.update(get_flat_parameter_dict(parameter.get("subField")))
            # for sub_parameter in parameter.get("subField"):
            #     if sub_parameter.get("id"):
            #         result[sub_parameter.get("id")] = sub_parameter

        else:
            result[parameter.get("id")] = parameter
    return result


async def validate_values(
    db_session: AsyncSession,
    parameters_input: schemas.RecipeBasicParameterInput,
):

    p_types = [ParameterType.primary, ParameterType.secondary, ParameterType.analytical]
    error_msg = ""
    error_dict = {}
    infos_dict = {}
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
            infos_dict[parameter_id] = {
                "result": result,
                "path": path["path"],
                "component": path["component"],
            }
        except ValueError as e:
            error_msg += f"Parameter {parameter_id} has invalid value {value}.\n"
            error_dict[parameter_id] = str(e)

    return error_dict, infos_dict


def convert_disease_option_label(
    option: schemas.MeasureDiseaseOption,
) -> schemas.MeasureDiseaseOption:
    if option.label == "全部":
        option.label = option.label + option.category_name
        return option
    return option


def get_chart_disease_z_options(loaded_value, disease_options_dict):
    if isinstance(loaded_value, list):
        if all([isinstance(e, str) for e in loaded_value]):
            options = [
                convert_disease_option_label(py_.get(disease_options_dict, e))
                for e in loaded_value
            ]
            options = [
                {
                    "value": f"{e.category_id}:{e.value}",
                    "label": e.label,
                    "category_id": e.category_id,
                }
                for e in options
            ]
            return options
        elif all([isinstance(e, dict) for e in loaded_value]):
            options = []
            for e in loaded_value:
                includes = e.get("include", [])
                excludes = e.get("exclude", [])
                include_label = convert_disease_option_label(
                    py_.get(disease_options_dict, includes[0]),
                ).label
                exclude_labels = ", ".join(
                    [
                        convert_disease_option_label(
                            py_.get(disease_options_dict, e),
                        ).label
                        for e in excludes
                    ],
                )
                options.append(
                    {"value": e, "label": f"{include_label}-{exclude_labels}"},
                )
            return options
    return []


def get_chart_pulse_z_options(loaded_value, pulse_options_dict):
    if isinstance(loaded_value, list):
        if all([isinstance(e, str) for e in loaded_value]):
            return [py_.get(pulse_options_dict, e) for e in loaded_value]
        elif all([isinstance(e, list) for e in loaded_value]):
            labels = []
            for pair in loaded_value:
                labels.append(
                    {
                        "value": pair,
                        "label": "+".join(
                            [py_.get(pulse_options_dict, f"{e}.label") for e in pair],
                        ),
                    },
                )
            return labels
    return []


def get_labels(options):
    labels = []
    for option in options:
        if isinstance(option, str):
            labels.append(option)
        elif isinstance(option, dict):
            labels.append(option.get("label"))
        elif hasattr(option, "label"):
            labels.append(getattr(option, "label"))

    return labels
