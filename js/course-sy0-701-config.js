// Course configuration for SY0-701
const courseConfig = {
    id: 'sy0-701',
    title: 'CompTIA Security+ SY0-701',
    topics: {
        'General Security Concepts': {
            weight: 0.12, // Placeholder weight
            file: '../data/sy0-701/general-security-concepts.json',
            description: 'Covers fundamental concepts of security, risk management, and controls.'
        },
        'Threats': {
            weight: 0.22, // Placeholder weight
            file: '../data/sy0-701/threats-vulnerabilities-mitigations.json',
            description: 'Focuses on analyzing and responding to threats, attacks, and vulnerabilities.'
        },
        'Security Architecture': {
            weight: 0.18, // Placeholder weight
            file: '../data/sy0-701/security-architecture.json',
            description: 'Includes the design and implementation of secure networks, systems, and applications.'
        },
        'Security Operations': {
            weight: 0.28, // Placeholder weight
            file: '../data/sy0-701/security-operations.json',
            description: 'Covers incident response, forensics, and disaster recovery.'
        },
        'Security Program Management': {
            weight: 0.20, // Placeholder weight
            file: '../data/sy0-701/security-program-management-oversight.json',
            description: 'Focuses on governance, risk management, and compliance.'
        }
    },
    examDuration: 5400, // 90 minutes in seconds
    examQuestionCount: 90, // Max 90 questions for a simulated exam
    passingScore: 750, // Passing score out of 900 for SY0-701
    maxScore: 900,
    description: 'The CompTIA Security+ SY0-701 exam covers the latest trends and techniques in risk management, risk mitigation, threat management and intrusion detection.'
};

async function updateTopicCounts() {
    console.log('Updating topic counts for SY0-701...');
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
