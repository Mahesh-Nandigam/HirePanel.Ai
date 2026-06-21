const candidates = [
    {
        name: "Mahesh Nandigam",
        role: "AI Engineer",
        finalScore: 92,
        github: 9.5,
        linkedin: 8.0,
        resume: 9.2,
        jdMatch: 9.5,
        status: "HIRE",
        avatar: "https://ui-avatars.com/api/?name=Mahesh+Nandigam&background=0D8ABC&color=fff",
        strengths: ["Built real agentic systems", "Global hackathon winner", "Strong AWS/Docker execution"],
        messages: [
            { agent: "Intake", text: "Successfully parsed Mahesh's resume and extracted GitHub/LinkedIn links." },
            { agent: "GitHub", text: "Stellar profile. 500+ commits this year, deep AI repositories." },
            { agent: "LinkedIn", text: "Career progression is solid. Fast riser." },
            { agent: "Resume", text: "10/10 execution. He actually builds things, no buzzword fluff." },
            { agent: "Decider", text: "Consensus reached. Mahesh is a 10x builder. Strong Hire." }
        ]
    },
    {
        name: "Shiva Kumar Reddy",
        role: "Junior Full Stack",
        finalScore: 65,
        github: 3.5,
        linkedin: 5.5,
        resume: 5.0,
        jdMatch: 6.0,
        status: "WAITLIST",
        avatar: "https://ui-avatars.com/api/?name=Shiva+Kumar&background=F59E0B&color=fff",
        strengths: ["Strong academics (10.0 SSC)", "Early internship experience", "Honest about skill levels"],
        messages: [
            { agent: "Intake", text: "Parsed Shiva's resume." },
            { agent: "GitHub", text: "Standard student profile. Basic academic repos." },
            { agent: "LinkedIn", text: "Secured junior internship early. Good baseline stability." },
            { agent: "Resume", text: "Solid foundational skills. ML project shows promise but lacks deployment metrics." },
            { agent: "Decider", text: "Good junior candidate, but needs more complex projects. Waitlist." }
        ]
    },
    {
        name: "Alex The Inflator",
        role: "Senior React Developer",
        finalScore: 32,
        github: 1.0,
        linkedin: 2.5,
        resume: 3.0,
        jdMatch: 2.0,
        status: "REJECT",
        avatar: "https://ui-avatars.com/api/?name=Alex+Inflator&background=EF4444&color=fff",
        strengths: ["Lists 50+ modern frameworks"],
        messages: [
            { agent: "Intake", text: "Parsed Alex's 4-page resume." },
            { agent: "GitHub", text: "Red flag. URL provided but 0 commits in the last 2 years." },
            { agent: "LinkedIn", text: "Job hopper. 5 jobs in 3 years. Title inflation detected." },
            { agent: "Resume", text: "Buzzword collector. Lists Kubernetes but no evidence of deployment." },
            { agent: "Decider", text: "Unanimous reject. High flight risk and lacks actual execution proof." }
        ]
    }
];
