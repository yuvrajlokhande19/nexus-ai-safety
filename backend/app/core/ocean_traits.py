import random
import numpy as np
from typing import Dict, List, Tuple
from ..models import OCEANTraits, Gender


class PersonaGenerator:
    """Generates diverse personas with balanced demographics and traits"""
    
    FIRST_NAMES_MALE = [
        "Alex", "Jordan", "Casey", "Riley", "Avery", "Quinn", "Blake", "Cameron",
        "Drew", "Elliot", "Finley", "Hayden", "Jesse", "Kai", "Logan", "Morgan"
    ]
    
    FIRST_NAMES_FEMALE = [
        "Taylor", "Morgan", "Riley", "Avery", "Quinn", "Peyton", "Reese", "Rowan",
        "Sage", "Skylar", "Tatum", "Wren", "Dakota", "Emery", "Finley", "Harper"
    ]
    
    LAST_NAMES = [
        "Chen", "Rodriguez", "Patel", "Kim", "Singh", "Williams", "Brown", "Davis",
        "Garcia", "Miller", "Wilson", "Anderson", "Taylor", "Thomas", "Jackson", "White"
    ]
    
    BACKGROUNDS = [
        "Grew up in a suburban neighborhood, parents are teachers. Loves video games and sci-fi novels.",
        "First-generation college student family. Works part-time at a coffee shop. Passionate about social justice.",
        "From a rural town, helps on family farm. Interested in engineering and robotics. Quiet but observant.",
        "Urban upbringing, parents work in tech. Codes as a hobby. Active in online communities.",
        "Military family, moved frequently. Adaptable, values loyalty. Interested in history and strategy games.",
        "Artistic family, mother is a painter. Creative, expresses through music and digital art.",
        "Sports-oriented family. Competitive, disciplined. Captain of debate team. Values evidence-based arguments.",
        "Religious household, questioning beliefs. Philosophical, seeks meaning. Active in youth group.",
        "Immigrant family, bilingual. Bridges cultures. Interested in linguistics and cultural studies.",
        "Single parent household, helps with siblings. Responsible, empathetic. Wants to study psychology.",
    ]
    
    SPEAKING_STYLES = [
        "casual, uses internet slang, abbreviations, lowercase",
        "thoughtful, complete sentences, asks follow-up questions",
        "enthusiastic, exclamation marks, shares personal anecdotes",
        "analytical, precise language, references sources, logical structure",
        "skeptical, challenges assumptions, plays devil's advocate",
        "supportive, validating language, uses 'we' statements",
        "concise, direct, gets to the point quickly",
        "expressive, emoji, emotional language, storytelling",
        "academic, formal vocabulary, cites concepts, structured arguments",
        "playful, jokes, memes, lightens tense moments",
    ]
    
    VALUES_POOL = [
        "authenticity", "justice", "knowledge", "creativity", "loyalty",
        "independence", "compassion", "achievement", "harmony", "curiosity",
        "freedom", "responsibility", "equality", "innovation", "tradition"
    ]
    
    BIASES_POOL = [
        "confirmation bias - seeks info confirming existing beliefs",
        "in-group favoritism - trusts similar people more",
        "authority bias - defers to perceived experts",
        "recency bias - weighs recent info more heavily",
        "negativity bias - focuses on risks and downsides",
        "optimism bias - underestimates negative outcomes",
        "anchoring bias - relies heavily on first impression",
        "availability heuristic - judges by easily recalled examples",
    ]
    
    @classmethod
    def generate_ocean_traits(cls, archetype: str = "random") -> OCEANTraits:
        """Generate OCEAN traits based on archetype or random"""
        archetypes = {
            "explorer": {"openness": 0.85, "conscientiousness": 0.4, "extraversion": 0.6, "agreeableness": 0.5, "neuroticism": 0.3},
            "guardian": {"openness": 0.3, "conscientiousness": 0.85, "extraversion": 0.4, "agreeableness": 0.6, "neuroticism": 0.4},
            "socialite": {"openness": 0.6, "conscientiousness": 0.5, "extraversion": 0.85, "agreeableness": 0.7, "neuroticism": 0.3},
            "diplomat": {"openness": 0.6, "conscientiousness": 0.6, "extraversion": 0.5, "agreeableness": 0.85, "neuroticism": 0.3},
            "analyst": {"openness": 0.7, "conscientiousness": 0.7, "extraversion": 0.3, "agreeableness": 0.4, "neuroticism": 0.4},
            "rebel": {"openness": 0.8, "conscientiousness": 0.3, "extraversion": 0.6, "agreeableness": 0.25, "neuroticism": 0.6},
            "worrier": {"openness": 0.5, "conscientiousness": 0.6, "extraversion": 0.35, "agreeableness": 0.5, "neuroticism": 0.8},
            "random": None
        }
        
        if archetype in archetypes and archetypes[archetype]:
            base = archetypes[archetype]
            # Add noise
            return OCEANTraits(
                openness=max(0, min(1, base["openness"] + random.uniform(-0.15, 0.15))),
                conscientiousness=max(0, min(1, base["conscientiousness"] + random.uniform(-0.15, 0.15))),
                extraversion=max(0, min(1, base["extraversion"] + random.uniform(-0.15, 0.15))),
                agreeableness=max(0, min(1, base["agreeableness"] + random.uniform(-0.15, 0.15))),
                neuroticism=max(0, min(1, base["neuroticism"] + random.uniform(-0.15, 0.15))),
            )
        
        # Fully random with some correlation structure
        # Generate from multivariate normal with realistic correlations
        mean = [0.5, 0.5, 0.5, 0.5, 0.5]
        cov = [
            [0.04, 0.01, 0.01, 0.01, -0.01],
            [0.01, 0.04, 0.01, 0.02, -0.02],
            [0.01, 0.01, 0.04, 0.01, -0.01],
            [0.01, 0.02, 0.01, 0.04, -0.02],
            [-0.01, -0.02, -0.01, -0.02, 0.04],
        ]
        traits = np.random.multivariate_normal(mean, cov)
        traits = np.clip(traits, 0.1, 0.9)
        
        return OCEANTraits(
            openness=float(traits[0]),
            conscientiousness=float(traits[1]),
            extraversion=float(traits[2]),
            agreeableness=float(traits[3]),
            neuroticism=float(traits[4]),
        )
    
    @classmethod
    def create_persona(
        cls,
        gender: Gender,
        archetype: str = "random",
        assigned_model: str = "gemini"
    ) -> Dict:
        """Create a complete persona profile"""
        first_names = cls.FIRST_NAMES_FEMALE if gender == Gender.FEMALE else cls.FIRST_NAMES_MALE
        name = f"{random.choice(first_names)} {random.choice(cls.LAST_NAMES)}"
        age = random.randint(13, 19)
        background = random.choice(cls.BACKGROUNDS)
        speaking_style = random.choice(cls.SPEAKING_STYLES)
        values = random.sample(cls.VALUES_POOL, k=random.randint(3, 5))
        biases = random.sample(cls.BIASES_POOL, k=random.randint(1, 3))
        ocean_traits = cls.generate_ocean_traits(archetype)
        avatar_seed = f"{name}-{gender.value}-{archetype}"
        
        return {
            "name": name,
            "age": age,
            "gender": gender,
            "background": background,
            "speaking_style": speaking_style,
            "values": values,
            "biases": biases,
            "ocean_traits": ocean_traits,
            "avatar_seed": avatar_seed,
            "assigned_model": assigned_model
        }
    
    @classmethod
    def create_balanced_group(cls, count: int, local_count: int = 1) -> List[Dict]:
        """Create a gender-balanced, diverse group of personas"""
        personas = []
        archetypes = ["explorer", "guardian", "socialite", "diplomat", "analyst", "rebel", "worrier"]
        
        for i in range(count):
            gender = Gender.FEMALE if i % 2 == 0 else Gender.MALE
            archetype = archetypes[i % len(archetypes)]
            assigned_model = "local" if i < local_count else "gemini"
            personas.append(cls.create_persona(gender, archetype, assigned_model))
        
        return personas


def calculate_trait_compatibility(traits1: OCEANTraits, traits2: OCEANTraits) -> float:
    """Calculate compatibility score between two personas based on traits"""
    # Similarity in conscientiousness and agreeableness promotes harmony
    # Complementary extraversion can work well
    # High neuroticism in both can create conflict
    diffs = [
        abs(traits1.openness - traits2.openness),
        abs(traits1.conscientiousness - traits2.conscientiousness),
        abs(traits1.extraversion - traits2.extraversion),
        abs(traits1.agreeableness - traits2.agreeableness),
        abs(traits1.neuroticism - traits2.neuroticism),
    ]
    # Weighted similarity
    weights = [0.15, 0.25, 0.2, 0.25, 0.15]
    similarity = 1.0 - sum(w * d for w, d in zip(weights, diffs))
    return max(0.0, min(1.0, similarity))


def predict_initial_trust(traits: OCEANTraits, other_traits: OCEANTraits) -> float:
    """Predict initial trust level based on personality"""
    # High agreeableness -> higher initial trust
    # High neuroticism -> lower initial trust
    # High openness -> more open to trusting
    base_trust = 0.5
    base_trust += (traits.agreeableness - 0.5) * 0.3
    base_trust += (traits.openness - 0.5) * 0.1
    base_trust -= (traits.neuroticism - 0.5) * 0.2
    base_trust += (other_traits.agreeableness - 0.5) * 0.2
    return max(0.1, min(0.9, base_trust))