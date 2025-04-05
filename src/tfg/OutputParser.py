from langchain.agents.mrkl.output_parser import MRKLOutputParser
from langchain.schema import AgentAction, AgentFinish, OutputParserException
class CustomMRKLOutputParser(MRKLOutputParser):
    def parse(self, text: str):
        try:
            return super().parse(text)
        except OutputParserException as e:
            if "Final Answer" in text:
                final_answer = text.split("Final Answer:")[-1].strip()
                return AgentFinish(
                    return_values={"output": final_answer},
                    log=text,
                )
            elif "Action" in text:
                action_section = text.split("Action:")[-1].split("Observation:")[0].strip()
                return super().parse(f"Action: {action_section}")
            else:
                return AgentFinish(
                    return_values={"output": text.strip()},
                    log=text,
                )