# https://www.notion.so/auohealth/623deca889324926ba1e6a3911472b82?pvs=4

from uuid import UUID

from sqlmodel import select

from auo_project import crud, models, schemas
from auo_project.core.constants import MAX_DEPTH_RATIO
from auo_project.core.file import get_max_amp_depth_of_range
from auo_project.db.session import SessionLocal


async def step2_update_calculated_columns(db_session, measure_id: UUID):
    measure_info = await crud.measure_info.get(db_session=db_session, id=measure_id)
    measure_info_in = schemas.MeasureInfoUpdate(
        mean_prop_range_max_l_cu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_cu,
            static_range_end_hand_position=measure_info.static_range_end_l_cu,
            static_max_amp_hand_position=measure_info.static_max_amp_l_cu,
            ratio=MAX_DEPTH_RATIO,
        ),
        mean_prop_range_max_l_qu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_qu,
            static_range_end_hand_position=measure_info.static_range_end_l_qu,
            static_max_amp_hand_position=measure_info.static_max_amp_l_qu,
            ratio=MAX_DEPTH_RATIO,
        ),
        mean_prop_range_max_l_ch=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_ch,
            static_range_end_hand_position=measure_info.static_range_end_l_ch,
            static_max_amp_hand_position=measure_info.static_max_amp_l_ch,
            ratio=MAX_DEPTH_RATIO,
        ),
        mean_prop_range_max_r_cu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_cu,
            static_range_end_hand_position=measure_info.static_range_end_r_cu,
            static_max_amp_hand_position=measure_info.static_max_amp_r_cu,
            ratio=MAX_DEPTH_RATIO,
        ),
        mean_prop_range_max_r_qu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_qu,
            static_range_end_hand_position=measure_info.static_range_end_r_qu,
            static_max_amp_hand_position=measure_info.static_max_amp_r_qu,
            ratio=MAX_DEPTH_RATIO,
        ),
        mean_prop_range_max_r_ch=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_ch,
            static_range_end_hand_position=measure_info.static_range_end_r_ch,
            static_max_amp_hand_position=measure_info.static_max_amp_r_ch,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_l_cu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_cu,
            static_range_end_hand_position=measure_info.static_range_end_l_cu,
            static_max_amp_hand_position=measure_info.static_max_amp_l_cu,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_l_qu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_qu,
            static_range_end_hand_position=measure_info.static_range_end_l_qu,
            static_max_amp_hand_position=measure_info.static_max_amp_l_qu,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_l_ch=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_l_ch,
            static_range_end_hand_position=measure_info.static_range_end_l_ch,
            static_max_amp_hand_position=measure_info.static_max_amp_l_ch,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_r_cu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_cu,
            static_range_end_hand_position=measure_info.static_range_end_r_cu,
            static_max_amp_hand_position=measure_info.static_max_amp_r_cu,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_r_qu=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_qu,
            static_range_end_hand_position=measure_info.static_range_end_r_qu,
            static_max_amp_hand_position=measure_info.static_max_amp_r_qu,
            ratio=MAX_DEPTH_RATIO,
        ),
        max_amp_depth_of_range_r_ch=get_max_amp_depth_of_range(
            static_range_start_hand_position=measure_info.static_range_start_r_ch,
            static_range_end_hand_position=measure_info.static_range_end_r_ch,
            static_max_amp_hand_position=measure_info.static_max_amp_r_ch,
            ratio=MAX_DEPTH_RATIO,
        ),
    )
    measure_info = await crud.measure_info.update(
        db_session=db_session,
        obj_current=measure_info,
        obj_new=measure_info_in,
    )


async def run_all_measures():
    db_session = SessionLocal()
    result = await db_session.execute(select(models.MeasureInfo.id).distinct())
    measure_ids = result.scalars().all()
    error_files = []
    for measure_id in measure_ids:
        print("measure_id", measure_id)
        try:
            await step2_update_calculated_columns(db_session, measure_id)
        except Exception as e:
            error_files.append((measure_id, e))
