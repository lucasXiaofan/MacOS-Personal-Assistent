// --- USER CONFIGURATION ---
const USER_CONFIG = {
    name: "Lucas (XiaoFan Lu)",
    dob: "2002-08-24", // YYYY-MM-DD
    master_start: "2025-09-01",
    master_end: "2027-06-01",
    life_expectancy_years: 80,
    peak_youth_end_age: 35
};

// --- QUOTES DATABASE ---
const QUOTES_DB = {
    "wake_up": [
        {
            "en": "The key is not to prioritize what's on your schedule, but to schedule your priorities.",
            "cn": "重点不在于安排日程表上的琐事，而在于安排你生活的优先级。",
            "source": "Stephen Covey (7 Habits)"
        },
        {
            "en": "Most of us spend too much time on what is urgent and not enough time on what is important.",
            "cn": "我们大多数人花太多时间在紧急的事情上，而花在重要事情上的时间却不够。",
            "source": "Stephen Covey (7 Habits)"
        },
        {
            "en": "I am not a product of my circumstances. I am a product of my decisions.",
            "cn": "我不是环境的产物。我是我决定的产物。",
            "source": "Stephen Covey (7 Habits)"
        },
        {
            "en": "You have wasted 23 years looking for a path. Walk the one you are on.",
            "cn": "你已经花了23年寻找道路。走你现在的路，别看了。",
            "source": "Lucas's Conscience"
        },
        {
            "en": "As if you could kill time without injuring eternity.",
            "cn": "你以为你可以消磨时间而不损害永恒吗？",
            "source": "Thoreau"
        },
        {
            "en": "Where is the discipline? Where is the 'Iron Performer'?",
            "cn": "自律在哪里？那个‘钢铁执行者’去哪了？",
            "source": "Self-Reflection"
        },
        {
            "en": "Most humans are never fully present in the now, because unconsciously they believe that the next moment must be more important than this one.",
            "cn": "大多数人从未完全活在当下，因为他们潜意识里认为下一刻比这一刻更重要。",
            "source": "Eckhart Tolle (Power of Now)"
        }
    ],
    "sarcasm": [
        {
            "en": "Oh, look who's back. Are you going to work or just stare at this?",
            "cn": "哟，看看谁回来了。你是要工作还是就盯着这个看？",
            "source": "System"
        },
        {
            "en": "Another day, another excuse to check YouTube?",
            "cn": "又是新的一天，又是新的借口看YouTube？",
            "source": "System"
        },
        {
            "en": "Your parents are aging while you refresh this page.",
            "cn": "当你刷新这个页面时，你的父母正在变老。",
            "source": "Reality"
        },
        {
            "en": "You have overdue tasks. I can smell the procrastination from here.",
            "cn": "你有过期的任务。我在这里都能闻到拖延的味道。",
            "source": "System"
        },
        {
            "en": "Are you building your AI agent or just dreaming about it?",
            "cn": "你是在构建你的AI Agent，还是只是在做梦？",
            "source": "Career Reality"
        }
    ],
    "inspire": [
        {
            "en": "Realize deeply that the present moment is all you have.",
            "cn": "深刻地认识到，当下是你所拥有的唯一。",
            "source": "Eckhart Tolle (Power of Now)"
        },
        {
            "en": "Effective people are not problem-minded; they are opportunity-minded.",
            "cn": "高效能人士不关注问题，他们关注机会。",
            "source": "Stephen Covey"
        },
        {
            "en": "A warrior does not give up what he loves, he finds the love in what he does.",
            "cn": "战士不会放弃他所爱的，他在他所做的事中找到爱。",
            "source": "Dan Millman (Way of the Peaceful Warrior)"
        },
        {
            "en": "The warrior's way is not about imagined perfection or victory; it is about love.",
            "cn": "战士之道无关想象中的完美或胜利；它关乎爱。",
            "source": "Dan Millman"
        },
        {
            "en": "Discipline is the bridge between goals and accomplishment.",
            "cn": "自律是连接目标与成就的桥梁。",
            "source": "Jim Rohn"
        },
        {
            "en": "Motivation gets you going, but discipline keeps you growing.",
            "cn": "动力让你开始，但自律让你成长。",
            "source": "John C. Maxwell"
        }
    ],
    "bible": [
        {
            "en": "Redeeming the time, because the days are evil.",
            "cn": "要爱惜光阴，因为现今的世代邪恶。",
            "source": "Ephesians 5:16"
        },
        {
            "en": "No temptation has overtaken you except such as is common to man; but God is faithful, who will not allow you to be tempted beyond what you are able.",
            "cn": "你们所遇见的试探，无非是人所能受的。神是信实的，必不叫你们受试探过于所能受的。",
            "source": "1 Corinthians 10:13"
        },
        {
            "en": "Flee also youthful lusts; but pursue righteousness, faith, love, peace with those who call on the Lord out of a pure heart.",
            "cn": "你要逃避少年的私欲，同那清心祷告主的人追求公义、信德、仁爱、和平。",
            "source": "2 Timothy 2:22"
        },
        {
            "en": "I have made a covenant with my eyes; Why then should I look upon a young woman?",
            "cn": "我与眼睛立约，怎能恋恋瞻望处女呢？",
            "source": "Job 31:1"
        },
        {
            "en": "Walk by the Spirit, and you will not gratify the desires of the flesh.",
            "cn": "你们当顺着圣灵而行，就不放纵肉体的情欲了。",
            "source": "Galatians 5:16"
        }
    ],
    "self_control": [
        {
            "en": "Porn is taking, Relationship is interacting. Don't castrate yourself into a statue.",
            "cn": "色情是索取，恋爱是交互。不要把自己阉割成一个毫无弱点的雕像。",
            "source": "Lucas's Reflection"
        },
        {
            "en": "You pay $50k/year at UMass not to watch YouTube.",
            "cn": "你在UMass一年交5万美金不是为了来看YouTube的。",
            "source": "Financial Reality"
        },
        {
            "en": "Defeat the urge now, and you will defeat it easier in the future.",
            "cn": "战胜现在的想法，未来也会更容易战胜。",
            "source": "Lucas's Reflection"
        },
        {
            "en": "Life has 90% more to offer than lust. Enjoy movement, thinking, and connection.",
            "cn": "人生至少90%的时间是绝对和色色完全没有关系的。享受运动、思考和交流。",
            "source": "Lucas's Reflection"
        },
        {
            "en": "Guilt comes after, but Awe comes during. Pray immediately.",
            "cn": "罪恶感通常产生于事后，但敬畏感产生于当下。立刻祷告。",
            "source": "Emergency Protocol"
        }
    ]
};
