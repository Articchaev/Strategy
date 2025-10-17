"""High-level strategy code"""

# !v DEBUG ONLY
import math  # type: ignore
from time import time  # type: ignore
from typing import Optional

from bridge import const
from bridge.auxiliary import aux, fld, rbt  # type: ignore
from bridge.const import State as GameStates
from bridge.router.base_actions import Action, Actions, KickActions  # type: ignore


class Strategy:
    """Main class of strategy"""

    def __init__(
        self,
    ) -> None:
        self.we_active = False

    def process(self, field: fld.Field) -> list[Optional[Action]]:
        """Game State Management"""
        if field.game_state not in [GameStates.KICKOFF, GameStates.PENALTY]:
            if field.active_team in [const.Color.ALL, field.ally_color]:
                self.we_active = True
            else:
                self.we_active = False

        actions: list[Optional[Action]] = []
        for _ in range(const.TEAM_ROBOTS_MAX_COUNT):
            actions.append(None)

        if field.ally_color == const.COLOR:
            text = str(field.game_state) + "  we_active:" + str(self.we_active)
            field.strategy_image.print(aux.Point(600, 780), text, need_to_scale=False)
        match field.game_state:
            case GameStates.RUN:
                self.run(field, actions)
            case GameStates.TIMEOUT:
                pass
            case GameStates.HALT:
                return [None] * const.TEAM_ROBOTS_MAX_COUNT
            case GameStates.PREPARE_PENALTY:
                pass
            case GameStates.PENALTY:
                pass
            case GameStates.PREPARE_KICKOFF:
                pass
            case GameStates.KICKOFF:
                pass
            case GameStates.FREE_KICK:
                pass
            case GameStates.STOP:
                # The router will automatically prevent robots from getting too close to the ball
                self.run(field, actions)

        return actions

    def run(self, field: fld.Field, actions: list[Optional[Action]]) -> None:
        """
        ONE ITERATION of strategy
        NOTE: robots will not start acting until this function returns an array of actions,
              if an action is overwritten during the process, only the last one will be executed)

        Examples of getting coordinates:
        - field.allies[8].get_pos(): aux.Point -   coordinates  of the 8th  robot from the allies
        - field.enemies[14].get_angle(): float - rotation angle of the 14th robot from the opponents

        - field.ally_goal.center: Point - center of the ally goalt
        - field.enemy_goal.hull: list[Point] - polygon around the enemy goal area


        Examples of robot control:
        - actions[2] = Actions.GoToPoint(aux.Point(1000, 500), math.pi / 2)
                The robot number 2 will go to the point (1000, 500), looking in the direction π/2 (up, along the OY axis)

        - actions[3] = Actions.Kick(field.enemy_goal.center)
                The robot number 3 will hit the ball to 'field.enemy_goal.center' (to the center of the enemy goal)

        - actions[9] = Actions.BallGrab(0.0)
                The robot number 9 grabs the ball at an angle of 0.0 (it looks to the right, along the OX axis)
        """
        
        self.defender(field, actions)
        if field.ally_color == const.Color.BLUE:
            self.Kick(field, actions, False)



    def defender(self, field: fld.Field, actions: list[Optional[Action]]):
        vb = field.ball.get_vel()
        X = field.ball.get_pos()
        a = field.ally_goal.up
        b = field.ally_goal.down
        Defence = aux.get_line_intersection(X, X + vb, a + field.ally_goal.eye_forw*100, b + field.ally_goal.eye_forw*100, 'RS')
        Defence2 = aux.get_line_intersection(X, X+vb, a, field.ally_goal.eye_forw*100 + a)
        Defence3 = aux.get_line_intersection(X, X+vb, b, field.ally_goal.eye_forw*100 + b)
        if Defence!=None and vb.mag()>50:
            actions[field.gk_id] = Actions.GoToPointIgnore(Defence, field.ally_goal.eye_forw.arg())
        elif Defence2!=None and vb.mag()>50:
            actions[field.gk_id] = Actions.GoToPointIgnore(Defence2, field.ally_goal.eye_forw.arg())
        elif Defence3!=None and vb.mag()>50:
            actions[field.gk_id] = Actions.GoToPointIgnore(Defence3, field.ally_goal.eye_forw.arg())
        else:
            actions[field.gk_id] = Actions.GoToPointIgnore((a + b)/2 + field.ally_goal.eye_forw*100, field.ally_goal.eye_forw.arg())
        
            if aux.is_point_inside_poly(X, field.ally_goal.hull) == True:
                actions[field.gk_id] = Actions.Kick(aux.Point(0, 0))

    def Kick(self, field: fld.Field, actions: list[Optional[Action]], ally_enemy: bool, Index: int):
        A = aux.Point(0, 75)
        if ally_enemy == True:
            a = field.ally_goal.up
            b = field.ally_goal.down
            goal1 = a + A
            goal2 = b - A
        else:
            a = field.enemy_goal.up
            b = field.enemy_goal.down
            goal1 = a - A
            goal2 = b + A
        Enemy_Goalkeeper = field.enemies[field.enemy_gk_id].get_pos()
        attacker = field.ball.get_pos()
        angle1 = aux.get_angle_between_points(goal1, attacker, Enemy_Goalkeeper)
        angle2 = aux.get_angle_between_points(Enemy_Goalkeeper, attacker, goal2)
        if (abs(angle1)>abs(angle2)):
            actions[Index] = Actions.Kick(goal1)
            # field.strategy_image.draw_circle(goal1, (255, 0, 255), 20)
        else:
            actions[Index] = Actions.Kick(goal2)
            # field.strategy_image.draw_circle(goal2, (255, 0, 255), 20)
    def Pas(self, field: fld.Field, actions: list[Optional[Action]]):
        Atacker1 = field.allies[1].get_pos()
        Atacker2 = field.allies[2].get_pos()
        a = field.enemy_goal.up
        b = field.enemy_goal.down
        A = aux.Point(-1000, -100)
        goal1 = a - A
        goal2 = b + A
        Ball = field.ball.get_pos()
        if Ball.y() >= 0:
            
            actions[1] = Actions.Kick(Atacker2)
            actions[1] = Actions.GoToPoint(goal1)
            

        
        



        
