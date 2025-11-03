// Course configuration for CEH v13 (Certified Ethical Hacker)
const courseConfig = {
    id: 'ceh',
    title: 'CEH v13 - Certified Ethical Hacker',
    topics: {
        'Domain 1: Information Security and Ethical Hacking Fundamentals': {
            weight: 0.175, // 17.5% average (15-20%)
            file: '../data/CEH/domain01-fundamentals.json',
            description: 'Information security concepts, ethical hacking fundamentals, security controls, and compliance',
            domain: 1
        },
        'Domain 2: Footprinting and Reconnaissance': {
            weight: 0.175, // 17.5% average (15-20%)
            file: '../data/CEH/domain02-footprinting.json',
            description: 'Footprinting methodologies, reconnaissance techniques, and information gathering',
            domain: 2
        },
        'Domain 3: Scanning, Enumeration, and Vulnerability Analysis': {
            weight: 0.175, // 17.5% average (15-20%)
            file: '../data/CEH/domain03-scanning.json',
            description: 'Network scanning, enumeration techniques, and vulnerability assessment',
            domain: 3
        },
        'Domain 4: System Hacking and Post-Exploitation': {
            weight: 0.225, // 22.5% average (20-25%)
            file: '../data/CEH/domain04-system-hacking.json',
            description: 'System hacking techniques, privilege escalation, maintaining access, and covering tracks',
            domain: 4
        },
        'Domain 5: Web, Cloud, IoT, and Emerging Technologies': {
            weight: 0.225, // 22.5% average (20-25%)
            file: '../data/CEH/domain05-emerging-tech.json',
            description: 'Web application security, cloud security, IoT security, and emerging technologies',
            domain: 5
        }
    },
    examDuration: 14400, // 240 minutes (4 hours) in seconds
    examQuestionCount: 125, // CEH v13 exam: 125 questions
    passingScore: 70, // 70% passing score (88/125 questions)
    maxScore: 100,
    description: 'The CEH v13 exam covers ethical hacking and penetration testing across five domains with 125 multiple-choice questions in four hours.'
};

async function updateTopicCounts() {
    console.log('Updating topic counts for CEH v13...');
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
