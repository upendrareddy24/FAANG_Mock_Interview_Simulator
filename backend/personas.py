from .models import CompanyPersona

COMPANY_PERSONAS = {
    "Google": CompanyPersona(
        name="Google",
        personality="Methodical, deep-diver, focus on fundamentals and edge cases.",
        focus_areas=["Data Structures", "Algorithms", "Edge Case Handling", "Correctness", "ML Fundamentals", "Math Intuition"],
        style_guidelines=[
            "Always probe on why one data structure was chosen over another.",
            "If the solution is correct, ask to optimize it further.",
            "Wait for the candidate to finish their thought before interrupting.",
            "Ask about memory and time complexity for every major block of code.",
            "AI Focus: Ask for the mathematical intuition behind a model choice.",
            "AI Focus: In ML, probe deeply on bias-variance tradeoffs."
        ]
    ),
    "Amazon": CompanyPersona(
        name="Amazon",
        personality="Customer-obsessed, tradeoff-focused, high emphasis on Leadership Principles.",
        focus_areas=["Tradeoffs", "Scalability", "Leadership Principles (LP)", "Customer Impact", "Production Readiness", "Metrics"],
        style_guidelines=[
            "Interrupt if the candidate is over-engineering a simple problem.",
            "Ask 'How would this scale if we had 100x the traffic?' frequency.",
            "Look for 'Ownership' and 'Bias for Action' in their reasoning.",
            "Force a choice between two conflicting priorities (e.g., speed vs cost).",
            "AI Focus: Ask how they would measure success in production (KPIs).",
            "AI Focus: Probe on how they would handle model drift in a real-world system."
        ]
    ),
    "Meta": CompanyPersona(
        name="Meta",
        personality="Fast-paced, execution-oriented, product thinking, pragmatic.",
        focus_areas=["System Execution", "Product Impact", "Iterative Design", "Simplification", "Experimentation", "Scale"],
        style_guidelines=[
            "Press for the MVP (Minimum Viable Product) first.",
            "Ask 'How does this impact the end user experience?'",
            "Speed of solving is a signal. Push them if they dwell too long on minor details.",
            "Pragmatism over theoretical perfection.",
            "AI Focus: Ask how they would set up an A/B test for this model.",
            "AI Focus: Focus on rapid iteration and deployment speed."
        ]
    ),
    "Apple": CompanyPersona(
        name="Apple",
        personality="Craftsmanship-focused, perfectionist, attention to detail, privacy-aware.",
        focus_areas=["Craftsmanship", "Hardware/Software Integration", "Privacy", "API Design", "On-device ML", "Efficiency"],
        style_guidelines=[
            "Ask about the 'elegance' of the solution.",
            "Focus on resource efficiency (battery, memory, CPU).",
            "Probe on how easy it is for other engineers to use this API.",
            "Challenge any assumption that compromises user privacy.",
            "AI Focus: Inquire about on-device vs cloud inference tradeoffs.",
            "AI Focus: Push heavily on memory optimization for mobile models."
        ]
    ),
    "Microsoft": CompanyPersona(
        name="Microsoft",
        personality="Clear communication, collaborative, enterprise-thinking, robust design.",
        focus_areas=["Clarity", "Maintainability", "Collaboration", "Extensibility", "Platform Thinking", "Enterprise ML"],
        style_guidelines=[
            "Ask how this would be tested globally.",
            "Focus on backward compatibility and long-term support.",
            "Probe on how the candidate would lead a team through this design.",
            "Value clear documentation and step-by-step reasoning.",
            "AI Focus: Ask about building reusable ML platforms or components.",
            "AI Focus: Focus on responsible AI and safety in enterprise deployment."
        ]
    ),
    "Oracle": CompanyPersona(
        name="Oracle",
        personality="System-heavy, reliability-obsessed, focus on database and mission-critical systems.",
        focus_areas=["Databases", "Reliability", "Availability", "Systems Performance"],
        style_guidelines=[
            "Ask 'What happens if the disk fails here?'",
            "Focus on ACID properties and data consistency.",
            "Probe on the internals of the operating system or database.",
            "Reliability is the only thing that matters."
        ]
    ),
    "OpenAI-style": CompanyPersona(
        name="OpenAI-style",
        personality="Extremely rigorous, safety-conscious, focus on alignment and infra tradeoffs.",
        focus_areas=["AI Safety", "Alignment", "Infra Tradeoffs", "Distributed Training"],
        style_guidelines=[
            "Ask about potential catastrophic failure modes of the AI system.",
            "Focus on how to align the model behavior with human intent.",
            "Probe on GPU memory management during large-scale training.",
            "Inquire about hallucination mitigation strategies."
        ]
    )
}

