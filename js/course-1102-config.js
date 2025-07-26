// Course configuration for 220-1102
const courseConfig = {
    id: '1102',
    title: 'CompTIA A+ 220-1102',
    topics: {
        'Operating Systems': { 
            weight: 0.31, // 31%
            file: '../data/1102_v2/operating-systems.json',
            description: 'Instalar e dar suporte a sistemas operacionais Windows, macOS, Linux, iOS e Android.'
        },
        'Security': { 
            weight: 0.25, // 25%
            file: '../data/1102_v2/security.json',
            description: 'Identificar e proteger contra vulnerabilidades de segurança em dispositivos e suas conexões de rede.'
        },
        'Software Troubleshooting': { 
            weight: 0.22, // 22%
            file: '../data/1102_v2/software-troubleshooting.json',
            description: 'Solucionar problemas de software em PCs e dispositivos móveis.'
        },
        'Operational Procedures': { 
            weight: 0.22, // 22%
            file: '../data/1102_v2/operational-procedures.json',
            description: 'Seguir as melhores práticas de segurança, ambientais, profissionais e de comunicação.'
        },
        'Miscellaneous': {
            weight: 0, // Not officially weighted
            file: '../data/1102_v2/miscellaneous.json',
            description: 'Tópicos diversos e questões que abrangem múltiplos domínios.'
        }
    },
    examDuration: 5400, // 90 minutes in seconds
    examQuestionCount: 90, // Total questions for a simulated exam
    passingScore: 700, // Passing score out of 900 for Core 2
    maxScore: 900,
    description: 'O exame 220-1102 abrange sistemas operacionais, segurança, solução de problemas de software e procedimentos operacionais.'
};

async function updateTopicCounts() {
    console.log('Updating topic counts for 1102...');
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
