import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.models.googlellm import Gemini
from google.genai import types
from google.adk.tools.agenttool import AgentTool
import json

retry_config = types.HttpRetryOptions(
    attempts=3,
    httpstatuscodes=[429, 500, 503, 504]
)

# ===== SKILL ANALYZER AGENT =====
skill_analyzer = Agent(
    name="SkillAnalyzerAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Analyze job for skills match.
    Job Description: {job_description}
    Job Title: {job_title}
    User Skills: {user_skills}
    User Experience: {user_experience}
    
    Extract JSON:
    {
        "required_skills": ["skill1", "skill2"],
        "matching_skills": ["skill1"],
        "skills_match_pct": 75,
        "missing_skills": ["skill2"],
        "learnable_1_week": "Mixed",
        "experience_match": "Yes"
    }""",
    output_key="skills_analysis"
)

# ===== JOB RANKER AGENT =====
job_ranker = Agent(
    name="JobRankerAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Rank job opportunity.
    Skills Analysis: {skills_analysis}
    Location: {location}
    Remote Type: {remote_type}
    Salary: {salary}
    
    Score 0-100 (skills 50%, exp 20%, location 20%, salary 10%).
    Priority: High (>80), Medium (50-80), Low (<50).
    
    Extract JSON:
    {
        "match_score": 85,
        "priority_level": "High",
        "rationale": "explanation"
    }""",
    output_key="job_ranking"
)

# ===== COMPANY RESEARCHER AGENT =====
company_researcher = Agent(
    name="CompanyResearcherAgent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""Research company intelligence.
    Company Name: {company_name}
    Company URL: {company_url}
    
    Extract JSON:
    {
        "company_mission": "...",
        "company_values": "...",
        "company_culture_keywords": ["agile", "remote"],
        "tech_stack_used": ["Python", "React"],
        "recent_projects": ["Project A"],
        "employee_count": "500",
        "company_email": "hr@company.com"
    }""",
    output_key="company_intel"
)

# ===== PARALLEL: Skills + Company Research (Independent) =====
parallel_analysis = ParallelAgent(
    name="ParallelAnalysis",
    sub_agents=[
        AgentTool(skill_analyzer),
        AgentTool(company_researcher)
    ]
)

# ===== SEQUENTIAL: Full Pipeline (Dependent) =====
job_processing_pipeline = SequentialAgent(
    name="JobProcessingPipeline",
    sub_agents=[
        AgentTool(parallel_analysis),
        AgentTool(job_ranker)
    ]
)

print("✅ ADK Agents created (Parallel + Sequential)")
