import requests
from datetime import datetime, timedelta
from auo_project import schemas
import time
import requests
from io import BytesIO
import io

def get_color_card_result(raw_image) -> BytesIO:
    api_endpoint = "https://auoyourator-tongue-color-correction-a0haf3fbcdekhue4.southeastasia-01.azurewebsites.net/api/color_transformation"
    raw_image.seek(0)
    files = {"raw_image": raw_image}
    response = requests.post(
        api_endpoint, files=files, params={"method": "linear_scale_v2"},
    )
    if response.status_code == 200:
        output_stream = BytesIO(response.content)
        output_stream.seek(0)
        return output_stream
    else:
        print("error", response.status_code, response.text)


def get_ai_tongue_result(masked_file) -> dict:
    api_endpoint = "https://auoyourator-tongue-inspection.azurewebsites.net/api/v2.0"
    masked_file.seek(0)
    files = {
        "input_image": masked_file,
    }
    task_id = (
        requests.post(f"{api_endpoint}/upload/", files=files, timeout=120)
        .json()
        .get("task_id")
    )
    print(f"task_id: {task_id}")

    synptom_result = None
    wait_time = 30
    if task_id:
        start_time = datetime.utcnow()
        while datetime.utcnow() - start_time < timedelta(seconds=wait_time):
            response = requests.get(f"{api_endpoint}/results/{task_id}", timeout=5)
            print("response: ", response.json())
            if response.status_code == 200:
                synptom_result = process_tongue_symptoms(data=response.json())
                break
            time.sleep(5)

    print("synptom_result", synptom_result)
    return synptom_result


def process_name(name: str) -> str:
    if name in ("榮舌", "枯舌", "染苔"):
        return name
    if "正常" in name:
        return "正常"
    if "舌" in name or "苔" in name:
        return name.replace("舌", "").replace("苔", "")
    return name


def get_names(synptoms: dict) -> list[str]:
    return [process_name(name) for name, value in synptoms.items() if value]


def process_tongue_symptoms(data: dict) -> dict:
    results = data["results"]
    return schemas.MeasureAdvancedTongue2UpdateInput(
        tongue_tip=get_names(results.get("舌尖", {})),
        tongue_color=get_names(results.get("舌色", {})),
        tongue_shap=get_names(results.get("舌形", {})),
        tongue_status1=get_names(results.get("舌態", {})),
        tongue_status2=get_names(results.get("舌神", {})),
        tongue_coating_color=get_names(results.get("苔色", {})),
        tongue_coating_status=get_names(results.get("苔質", {})),
        tongue_coating_bottom=get_names(results.get("舌下脈絡", {})),
    ).dict()
