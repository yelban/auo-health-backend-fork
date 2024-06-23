from auo_project.crud.base_crud import CRUDBase
from auo_project.models.subject_tag_model import SubjectTag
from auo_project.schemas.subject_tag_schema import SubjectTagCreate, SubjectTagUpdate


class CRUDSubjectTag(CRUDBase[SubjectTag, SubjectTagCreate, SubjectTagUpdate]):
    async def get_options(self, db_session):
        raw_tags = await self.get_all(db_session=db_session)
        return self.format_options(raw_tags)

    def format_options(self, options):
        return [
            {
                "value": raw_tag.id,
                "key": raw_tag.name,
                "type": raw_tag.tag_type,
            }
            for raw_tag in options
        ]


subject_tag = CRUDSubjectTag(SubjectTag)
