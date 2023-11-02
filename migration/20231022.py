from uuid import UUID

from sqlmodel import select

from auo_project import crud, models, schemas
from auo_project.core.constants import MAX_DEPTH_RATIO
from auo_project.core.file import get_max_amp_depth_of_range
from auo_project.core.utils import get_measure_strength, get_measure_width, safe_divide
from auo_project.db.session import SessionLocal


async def step2_update_calculated_columns(db_session, measure_id: UUID):
    measure_info = await crud.measure_info.get(db_session=db_session, id=measure_id)
    width_value_l_cu = safe_divide(measure_info.range_length_l_cu, 0.2)
    width_value_l_qu = safe_divide(measure_info.range_length_l_qu, 0.2)
    width_value_l_ch = safe_divide(measure_info.range_length_l_ch, 0.2)
    width_value_r_cu = safe_divide(measure_info.range_length_r_cu, 0.2)
    width_value_r_qu = safe_divide(measure_info.range_length_r_qu, 0.2)
    width_value_r_ch = safe_divide(measure_info.range_length_r_ch, 0.2)
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
        strength_l_cu=get_measure_strength(
            measure_info.max_slope_value_l_cu,
            measure_info.max_amp_value_l_cu,
        ),
        strength_l_qu=get_measure_strength(
            measure_info.max_slope_value_l_qu,
            measure_info.max_amp_value_l_qu,
        ),
        strength_l_ch=get_measure_strength(
            measure_info.max_slope_value_l_ch,
            measure_info.max_amp_value_l_ch,
        ),
        strength_r_cu=get_measure_strength(
            measure_info.max_slope_value_r_cu,
            measure_info.max_amp_value_r_cu,
        ),
        strength_r_qu=get_measure_strength(
            measure_info.max_slope_value_r_qu,
            measure_info.max_amp_value_r_qu,
        ),
        strength_r_ch=get_measure_strength(
            measure_info.max_slope_value_r_ch,
            measure_info.max_amp_value_r_ch,
        ),
        width_l_cu=get_measure_width(
            measure_info.range_length_l_cu,
            measure_info.max_amp_value_l_cu,
            measure_info.max_slope_value_l_cu,
        ),
        width_l_qu=get_measure_width(
            measure_info.range_length_l_qu,
            measure_info.max_amp_value_l_qu,
            measure_info.max_slope_value_l_qu,
        ),
        width_l_ch=get_measure_width(
            measure_info.range_length_l_ch,
            measure_info.max_amp_value_l_ch,
            measure_info.max_slope_value_l_ch,
        ),
        width_r_cu=get_measure_width(
            measure_info.range_length_r_cu,
            measure_info.max_amp_value_r_cu,
            measure_info.max_slope_value_r_cu,
        ),
        width_r_qu=get_measure_width(
            measure_info.range_length_r_qu,
            measure_info.max_amp_value_r_qu,
            measure_info.max_slope_value_r_qu,
        ),
        width_r_ch=get_measure_width(
            measure_info.range_length_r_ch,
            measure_info.max_amp_value_r_ch,
            measure_info.max_slope_value_r_ch,
        ),
        width_value_l_cu=round(width_value_l_cu, 1) if width_value_l_cu else None,
        width_value_l_qu=round(width_value_l_qu, 1) if width_value_l_qu else None,
        width_value_l_ch=round(width_value_l_ch, 1) if width_value_l_ch else None,
        width_value_r_cu=round(width_value_r_cu, 1) if width_value_r_cu else None,
        width_value_r_qu=round(width_value_r_qu, 1) if width_value_r_qu else None,
        width_value_r_ch=round(width_value_r_ch, 1) if width_value_r_ch else None,
    )
    measure_info = await crud.measure_info.update(
        db_session=db_session,
        obj_current=measure_info,
        obj_new=measure_info_in,
    )


# run @ 20231022
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
