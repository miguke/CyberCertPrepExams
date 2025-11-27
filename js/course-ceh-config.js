// Course configuration for CEH v13 (Certified Ethical Hacker)
const courseConfig = {
    id: 'ceh',
    title: 'CEH v13 - Certified Ethical Hacker',
    topics: {
        'Module 01: Introduction to Ethical Hacking': {
            weight: 0.073, // 7.3% (22 questions out of 303)
            file: '../data/CEH/domain01-fundamentals.json',
            description: 'Information security concepts, ethical hacking fundamentals, information security controls, and laws',
            domain: 1
        },
        'Module 02: Footprinting and Reconnaissance': {
            weight: 0.129, // 12.9% (39 questions out of 303)
            file: '../data/CEH/domain02-footprinting-reconnaissance.json',
            description: 'Footprinting concepts, footprinting through search engines, web services, and social networking sites',
            domain: 2
        },
        'Module 03-04: Scanning Networks and Enumeration': {
            weight: 0.116, // 11.6% (35 questions out of 303)
            file: '../data/CEH/domain03-scanning-enumeration.json',
            description: 'Network scanning techniques, enumeration concepts, and vulnerability assessment',
            domain: 3
        },
        'Module 06: System Hacking': {
            weight: 0.046, // 4.6% (14 questions out of 303)
            file: '../data/CEH/domain04-system-hacking.json',
            description: 'Password cracking, privilege escalation, maintaining access, and clearing logs',
            domain: 4
        },
        'Module 07: Malware Threats': {
            weight: 0.063, // 6.3% (19 questions out of 303)
            file: '../data/CEH/domain05-malware-threats.json',
            description: 'Malware analysis, Trojans, viruses, worms, and APT threats',
            domain: 5
        },
        'Module 08: Sniffing': {
            weight: 0.030, // 3.0% (9 questions out of 303)
            file: '../data/CEH/domain06-sniffing.json',
            description: 'Packet sniffing techniques, MAC attacks, DHCP attacks, and ARP poisoning',
            domain: 6
        },
        'Module 09: Social Engineering': {
            weight: 0.040, // 4.0% (12 questions out of 303)
            file: '../data/CEH/domain07-social-engineering.json',
            description: 'Social engineering concepts, phishing, impersonation, and identity theft',
            domain: 7
        },
        'Module 10: Denial-of-Service': {
            weight: 0.033, // 3.3% (10 questions out of 303)
            file: '../data/CEH/domain08-denial-of-service.json',
            description: 'DoS/DDoS attack techniques, botnets, and DoS/DDoS countermeasures',
            domain: 8
        },
        'Module 11: Session Hijacking': {
            weight: 0.010, // 1.0% (3 questions out of 303)
            file: '../data/CEH/domain09-session-hijacking.json',
            description: 'Session hijacking concepts, application-level session hijacking, and countermeasures',
            domain: 9
        },
        'Module 12: Evading IDS, Firewalls, and Honeypots': {
            weight: 0.030, // 3.0% (9 questions out of 303)
            file: '../data/CEH/domain10-evading-ids-firewalls.json',
            description: 'IDS/IPS evasion techniques, firewall evasion, and honeypot detection',
            domain: 10
        },
        'Module 13: Hacking Web Servers': {
            weight: 0.026, // 2.6% (8 questions out of 303)
            file: '../data/CEH/domain11-hacking-web-servers.json',
            description: 'Web server attacks, web server attack methodology, and countermeasures',
            domain: 11
        },
        'Module 14: Hacking Web Applications': {
            weight: 0.059, // 5.9% (18 questions out of 303)
            file: '../data/CEH/domain12-hacking-web-applications.json',
            description: 'Web application vulnerabilities, OWASP Top 10, and web API attacks',
            domain: 12
        },
        'Module 15: SQL Injection': {
            weight: 0.050, // 5.0% (15 questions out of 303)
            file: '../data/CEH/domain13-sql-injection.json',
            description: 'SQL injection attacks, types of SQL injection, and evasion techniques',
            domain: 13
        },
        'Module 16: Hacking Wireless Networks': {
            weight: 0.076, // 7.6% (23 questions out of 303)
            file: '../data/CEH/domain14-hacking-wireless-networks.json',
            description: 'Wireless encryption, wireless threats, Bluetooth attacks, and wireless security tools',
            domain: 14
        },
        'Module 17: Hacking Mobile Platforms': {
            weight: 0.036, // 3.6% (11 questions out of 303)
            file: '../data/CEH/domain15-hacking-mobile-platforms.json',
            description: 'Mobile platform attack vectors, Android and iOS hacking, and mobile security guidelines',
            domain: 15
        },
        'Module 18: IoT and OT Hacking': {
            weight: 0.059, // 5.9% (18 questions out of 303)
            file: '../data/CEH/domain16-iot-ot-hacking.json',
            description: 'IoT hacking methodology, OT attacks, and IoT and OT security tools',
            domain: 16
        },
        'Module 19: Cloud Computing': {
            weight: 0.063, // 6.3% (19 questions out of 303)
            file: '../data/CEH/domain17-cloud-computing.json',
            description: 'Cloud computing concepts, container technologies, and cloud security',
            domain: 17
        },
        'Module 20: Cryptography': {
            weight: 0.063, // 6.3% (19 questions out of 303)
            file: '../data/CEH/domain18-cryptography.json',
            description: 'Encryption algorithms, cryptography tools, public key infrastructure (PKI), and cryptanalysis',
            domain: 18
        }
    },
    examDuration: 14400, // 240 minutes (4 hours) in seconds
    examQuestionCount: 125, // CEH v13 exam: 125 questions
    passingScore: 70, // 70% passing score (88/125 questions)
    maxScore: 100,
    description: 'The CEH v13 exam covers ethical hacking and penetration testing across 20 official modules with 125 multiple-choice questions in four hours.'
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
