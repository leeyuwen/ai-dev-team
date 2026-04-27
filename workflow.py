from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

class DevelopmentState(TypedDict):
    requirement: str
    architecture: str
    spec: str
    code: str
    test_report: str
    deployment_plan: str
    current_agent: str
    history: List[str]

def create_development_workflow():
    from agents import get_all_agents
    agents = get_all_agents()

    def architect_node(state):
        agent = agents["architect"]
        chain = agent["prompt"] | agent["llm"]
        result = chain.invoke({"requirement": state["requirement"], "spec": state["spec"]})
        return {
            "architecture": result.content,
            "current_agent": "架构师",
            "history": state["history"] + [f"架构师: {result.content}"]
        }

    def product_manager_node(state):
        agent = agents["product_manager"]
        chain = agent["prompt"] | agent["llm"]
        result = chain.invoke({"requirement": state["requirement"]})
        return {
            "spec": result.content,
            "current_agent": "产品经理",
            "history": state["history"] + [f"产品经理: {result.content}"]
        }

    def developer_node(state):
        agent = agents["developer"]
        chain = agent["prompt"] | agent["llm"]
        result = chain.invoke({"spec": state["spec"], "architecture": state["architecture"]})
        return {
            "code": result.content,
            "current_agent": "开发工程师",
            "history": state["history"] + [f"开发工程师: {result.content}"]
        }

    def tester_node(state):
        agent = agents["tester"]
        chain = agent["prompt"] | agent["llm"]
        result = chain.invoke({"spec": state["spec"], "code": state["code"]})
        return {
            "test_report": result.content,
            "current_agent": "测试工程师",
            "history": state["history"] + [f"测试工程师: {result.content}"]
        }

    def devops_node(state):
        agent = agents["devops"]
        chain = agent["prompt"] | agent["llm"]
        result = chain.invoke({"code": state["code"], "test_report": state["test_report"]})
        return {
            "deployment_plan": result.content,
            "current_agent": "部署工程师",
            "history": state["history"] + [f"部署工程师: {result.content}"]
        }

    workflow = StateGraph(DevelopmentState)

    workflow.add_node("architect", architect_node)
    workflow.add_node("product_manager", product_manager_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("tester", tester_node)
    workflow.add_node("devops", devops_node)

    workflow.add_edge("product_manager", "architect")
    workflow.add_edge("architect", "developer")
    workflow.add_edge("developer", "tester")
    workflow.add_edge("tester", "devops")
    workflow.add_edge("devops", END)

    workflow.set_entry_point("product_manager")

    memory = MemorySaver()
    compiled_workflow = workflow.compile(checkpointer=memory)

    return compiled_workflow

def run_development_workflow(requirement):
    workflow = create_development_workflow()

    initial_state = DevelopmentState(
        requirement=requirement,
        architecture="",
        spec="",
        code="",
        test_report="",
        deployment_plan="",
        current_agent="",
        history=[]
    )

    config = {"configurable": {"thread_id": "default"}}

    result = workflow.invoke(initial_state, config=config)
    return result