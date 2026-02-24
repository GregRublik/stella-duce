from models.goal_stage import GoalStage
from repositories.base import SQLAlchemyRepository


class GoalStageRepository(SQLAlchemyRepository):
    model = GoalStage
