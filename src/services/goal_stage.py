from repositories.goal_stage import GoalStageRepository
from models.goal_stage import StageStatus, GoalStage

from services.unit_of_work import UnitOfWork

class GoalStageService:

    def __init__(self, repository: GoalStageRepository, uow: UnitOfWork):
        self.repository = repository
        self.uow = uow

    @staticmethod
    def is_stage_ready(stage: GoalStage) -> bool:
        return all(
            dep.prerequisite_stage.status == StageStatus.COMPLETED
            for dep in stage.dependencies
        )
