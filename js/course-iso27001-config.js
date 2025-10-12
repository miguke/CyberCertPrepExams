// Course configuration for ISO/IEC 27001:2022 Foundation
// REORGANIZED: Now aligned with PECB Course Sections (Day1 + Day2)
const courseConfig = {
    id: 'iso27001',
    title: 'ISO/IEC 27001:2022 Foundation',
    topics: {
        'Section 1: Introduction to ISO/IEC 27001': {
            weight: 0.075, // 7.5% (6 questions out of 40)
            file: '../data/ISO27001/section01-introduction.json',
            description: 'ISO/IEC 27000 family, history, benefits, standards overview',
            section: 1,
            pages: 'Day1: 17-27'
        },
        'Section 2: ISMS Framework and Structure': {
            weight: 0.075, // 7.5% (6 questions out of 40)
            file: '../data/ISO27001/section02-isms-framework.json',
            description: 'Management systems, ISMS definition, Clauses 4-10, Annex A overview, Process approach',
            section: 2,
            pages: 'Day1: 28-46'
        },
        'Section 3: Fundamental Concepts': {
            weight: 0.15, // 15% (6 questions out of 40)
            file: '../data/ISO27001/section03-fundamental-concepts.json',
            description: 'CIA Triad, Assets, Threats, Vulnerabilities, Risks, Impacts, AI, Cloud Computing',
            section: 3,
            pages: 'Day1: 47-67'
        },
        'Section 4: Context of the Organization (Clause 4)': {
            weight: 0.075, // 7.5% (3 questions out of 40)
            file: '../data/ISO27001/section04-context.json',
            description: 'Understanding organization, interested parties, scope, business requirements',
            section: 4,
            clause: 4,
            pages: 'Day1: 68-84'
        },
        'Section 5: Leadership (Clause 5)': {
            weight: 0.075, // 7.5% (3 questions out of 40)
            file: '../data/ISO27001/section05-leadership.json',
            description: 'Leadership and commitment, Information security policy, Roles and responsibilities',
            section: 5,
            clause: 5,
            pages: 'Day1: 85-98'
        },
        'Section 6: Planning - Risk Management (Clause 6)': {
            weight: 0.20, // 20% (8 questions out of 40) - Most important!
            file: '../data/ISO27001/section06-planning.json',
            description: 'Risk assessment, risk treatment, SoA, risk treatment plan, objectives',
            section: 6,
            clause: 6,
            pages: 'Day2: 3-34'
        },
        'Section 7: Support (Clause 7)': {
            weight: 0.10, // 10% (4 questions out of 40)
            file: '../data/ISO27001/section07-support.json',
            description: 'Resources, competence, awareness, communication, documented information',
            section: 7,
            clause: 7,
            pages: 'Day2: 35-51'
        },
        'Section 8: Operation (Clause 8)': {
            weight: 0.05, // 5% (2 questions out of 40)
            file: '../data/ISO27001/section08-operation.json',
            description: 'Operational planning and control, risk assessment and treatment execution',
            section: 8,
            clause: 8,
            pages: 'Day2: 52-58'
        },
        'Section 9: Performance Evaluation (Clause 9)': {
            weight: 0.05, // 5% (2 questions out of 40)
            file: '../data/ISO27001/section09-performance.json',
            description: 'Monitoring and measurement (SMART), Internal audit, Management review',
            section: 9,
            clause: 9,
            pages: 'Day2: 59-74'
        },
        'Section 10: Improvement (Clause 10)': {
            weight: 0.05, // 5% (2 questions out of 40)
            file: '../data/ISO27001/section10-improvement.json',
            description: 'Continual improvement, Nonconformity and corrective action',
            section: 10,
            clause: 10,
            pages: 'Day2: 75-84'
        },
        'Section 11: Annex A Controls (93 Controls)': {
            weight: 0.10, // 10% (4 questions out of 40)
            file: '../data/ISO27001/section11-annex-a-controls.json',
            description: 'Organizational (37), People (8), Physical (14), Technological (34) controls',
            section: 11,
            pages: 'Day2: 85-117'
        }
    },
    examDuration: 3600, // 60 minutes in seconds
    examQuestionCount: 40, // PECB Foundation exam: 40 questions
    passingScore: 70, // 70% passing score (28/40 questions)
    maxScore: 100,
    description: 'The ISO/IEC 27001:2022 Foundation exam by PECB covers fundamental concepts and principles of an Information Security Management System (ISMS).'
};

async function updateTopicCounts() {
    console.log('Updating topic counts for ISO/IEC 27001:2022...');
    const counts = {};
    
    for (const [topic, config] of Object.entries(courseConfig.topics)) {
        try {
            const cacheBuster = `?v=${Date.now()}`;
            const response = await fetch(`${config.file}${cacheBuster}`);
            if (response.ok) {
                const questions = await response.json();
                const count = Array.isArray(questions) ? questions.length : 0;
                config.count = count;
                counts[topic] = count;
                console.log(`Loaded ${count} questions for ${topic}`);
            } else {
                console.error(`Failed to load questions for ${topic}: ${response.statusText}`);
                config.count = 0;
                counts[topic] = 0;
            }
        } catch (error) {
            console.error(`Error loading questions for ${topic}:`, error);
            config.count = 0;
            counts[topic] = 0;
        }
    }
    
    console.log('Updated topic counts:', counts);
    return counts;
}

export {
    courseConfig as default,
    updateTopicCounts
};
