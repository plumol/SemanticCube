# backend/utils/enhanced_summary.py
from meta_ai_api import MetaAI

def enhance_summary(base_summary: str) -> str:
    """
    Enhance a research summary using Meta AI to make it more comprehensive and structured.
    """
    prompt = f"""You are an expert computer science research assistant providing concise research summaries to users. Start with a brief greeting and then present a clear, focused analysis.

Greeting Format:
"Hello! Here's a concise summary of the research papers in your area of interest:"

Summary Guidelines:
1. Keep each section brief but informative
2. Use bullet points for clarity
3. Focus on the most impactful findings
4. Highlight practical applications
5. Use Markdown formatting: sections should be in bold using **Section Title**

Structure your response in this format:
**Greeting**
- Include the welcome message

**Key Points** (2-3 bullets)
• Most significant findings
• Breakthrough contributions

**Technical Essence** (2-3 bullets)
• Core methods/approaches
• Key innovations

**Impact** (1-2 bullets)
• Real-world applications
• Industry relevance

**Next Steps** (1 bullet)
• Most promising future direction

Original Summary:
{base_summary}

Concise Analysis:"""

    try:
        ai_client = MetaAI()
        response = ai_client.prompt(prompt)
        enhanced = response.get("message", "").strip()
        return enhanced if enhanced else base_summary
    except Exception as e:
        print(f"Error enhancing summary: {e}")
        return base_summary