"""LangGraph workflow skeleton."""

import logging
from langgraph.graph import StateGraph, END

from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.agents.critic import CriticAgent

logger = logging.getLogger(__name__)


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self) -> None:
        self.graph = self.build()

    def build(self) -> object:
        """Create a LangGraph graph.

        Implement nodes, edges, conditional routing, and stop condition.
        Suggested nodes: supervisor, researcher, analyst, writer, optional critic.
        """
        # 1. Khởi tạo StateGraph với State schema
        workflow = StateGraph(ResearchState)

        # 2. Thêm các nodes
        workflow.add_node("supervisor", lambda state: SupervisorAgent().run(state))
        workflow.add_node("researcher", lambda state: ResearcherAgent().run(state))
        workflow.add_node("analyst", lambda state: AnalystAgent().run(state))
        workflow.add_node("writer", lambda state: WriterAgent().run(state))
        workflow.add_node("critic", lambda state: CriticAgent().run(state))

        # 3. Đặt entry point
        workflow.set_entry_point("supervisor")

        # 4. Định nghĩa hàm routing
        def route_decision(state: ResearchState) -> str:
            if not state.route_history:
                logger.warning("route_history is empty, sending to supervisor node")
                return "supervisor"
            
            last_route = state.route_history[-1]
            if last_route == "done":
                return END
            return last_route

        # 5. Thêm conditional edges từ supervisor đi các node khác
        workflow.add_conditional_edges(
            "supervisor",
            route_decision,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                "critic": "critic",
                "done": END,
                END: END
            }
        )

        # 6. Thêm các edges quay ngược lại supervisor từ các worker agents
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")
        workflow.add_edge("critic", "supervisor")

        # 7. Compile graph
        return workflow.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state.

        Compile graph, invoke it, and convert result back to ResearchState.
        """
        logger.info("Starting Multi-Agent Workflow graph execution...")
        result = self.graph.invoke(state)

        # Trả về kết quả dưới dạng đối tượng ResearchState
        if isinstance(result, dict):
            return ResearchState(**result)
        return result

