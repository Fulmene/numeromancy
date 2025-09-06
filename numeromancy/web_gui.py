# web_gui.py
import streamlit as st
import sys
import io
import os
sys.path.append(os.path.dirname(__file__))

from deck_generator import generate_deck, is_nonland, is_in_color
import card
import data
from collections import Counter
import contextlib

# Initialize card data once using Streamlit cache
@st.cache_resource
def load_card_data():
    card_data = data.load(no_download=True)
    card.load_cards(card_data)
    all_cards = card.get_cards()
    name_to_card = {c.name: c for c in all_cards}
    return all_cards, name_to_card

# Context manager to capture stdout
@contextlib.contextmanager
def capture_stdout():
    new_out = io.StringIO()
    old_out = sys.stdout
    try:
        sys.stdout = new_out
        yield new_out
    finally:
        sys.stdout = old_out

def main():
    st.title("MTG Deck Generator")
    
    # Preset configurations
    presets = {
        "Monored (Emberheart Challenger)": {
            "starting_text": "Emberheart Challenger\n" * 4,
            "colors": ["Red (R)"],
            "mana_curve": [0, 16, 12, 8, 4, 0, 0, 0],
            "card_types": (30, 10, 20),
            "weights": (1.0, 1.0, 1.0, 1.0)
        },
        "Monogreen (Chocobo/Bill)": {
            "starting_text": "Traveling Chocobo\n"*4 + "Bristly Bill, Spine Sower\n"*4,
            "colors": ["Green (G)"],
            "mana_curve": [0, 12, 12, 8, 2, 0, 0, 0],
            "card_types": (26, 8, 26),
            "weights": (1.0, 1.0, 1.0, 1.0)
        },
        "Vivi Ornitier": {
            "starting_text": "Vivi Ornitier\n" *4,
            "colors": ["Blue (U)", "Red (R)"],
            "mana_curve": [0, 20, 12, 5, 1, 0, 0, 0],
            "card_types": (5, 33, 22),
            "weights": (1.0, 1.0, 1.0, 1.0)
        },
        "Dimir (Kaito)": {
            "starting_text": "Kaito, Bane of Nightmares\n"*4,
            "colors": ["Blue (U)", "Black (B)"],
            "mana_curve": [0, 8, 16, 8, 4, 0, 0, 0],
            "card_types": (24, 12, 24),
            "weights": (1.0, 1.0, 1.0, 1.0)
        },
        "Energy (Guide of Souls)": {
            "starting_text": "Guide of Souls\n"*4,
            "colors": ["White (W)", "Red (R)"],
            "mana_curve": [0, 16, 16, 8, 0, 0, 0, 0],
            "card_types": (28, 12, 20),
            "weights": (1.0, 1.0, 1.0, 1.0)
        },
        "Death & Taxes (Phelia)": {
            "starting_text": "Phelia, Exuberant Shepherd\n"*4,
            "colors": ["White (W)", "Black (B)"],
            "mana_curve": [0, 12, 12, 8, 4, 4, 0, 0],
            "card_types": (28, 12, 20),
            "weights": (1.0, 1.0, 1.0, 1.0)
        },
        "Phoenix (Arclight)": {
            "starting_text": "Arclight Phoenix\n"*4,
            "colors": ["Blue (U)", "Red (R)"],
            "mana_curve": [0, 27, 10, 1, 4, 0, 0, 0],
            "card_types": (9, 33, 18),
            "weights": (1.0, 1.0, 1.0, 1.0)
        },
    }
    
    # Preset selection
    preset_names = ["Custom"] + list(presets.keys())
    preset_name = st.selectbox("Configuration Preset", preset_names)
    
    # Load and map colors
    color_map = {
        "White (W)": "W", 
        "Blue (U)": "U", 
        "Black (B)": "B", 
        "Red (R)": "R", 
        "Green (G)": "G", 
        "Colorless (C)": "C"
    }
    
    # Load card data
    all_cards, name_to_card = load_card_data()
    
    # Section 1: Starting Cards
    st.header("Starting Cards")
    if preset_name != "Custom":
        preset = presets[preset_name]
        starting_input = st.text_area(
            "Starting cards (one name per line)", 
            value=preset["starting_text"],
            key="starting_cards"
        )
    else:
        starting_input = st.text_area(
            "Starting cards (one name per line)", 
            "Phelia, Exuberant Shepherd\n"*4,
            key="starting_cards"
        )
    
    starting_cards = []
    for line in starting_input.split("\n"):
        name = line.strip()
        if name and name in name_to_card:
            starting_cards.append(name_to_card[name])
        elif name:
            st.warning(f"Card not found: {name}")
    
    # Section 2: Color Selection
    st.header("Color Identity")
    if preset_name != "Custom":
        colors = st.multiselect(
            "Select deck colors", 
            color_map.keys(),
            default=preset["colors"],
            key="colors"
        )
    else:
        colors = st.multiselect(
            "Select deck colors", 
            color_map.keys(),
            default=["White (W)", "Black (B)"],
            key="colors"
        )
    color_symbols = [color_map[c] for c in colors]
    
    # Section 3: Mana Curve Configuration (Vertical Layout)
    st.header("Mana Curve")
    st.write("Configure the number of nonland cards at each mana value:")
    
    if preset_name != "Custom":
        curve_preset = preset["mana_curve"]
    else:
        curve_preset = [0, 12, 12, 8, 4, 4, 0, 0]  # DNT default
    
    mana_curve = []
    cmc_labels = ["0 cost", "1 mana", "2 mana", "3 mana", "4 mana", "5 mana", "6 mana", "7+ mana"]
    for i, label in enumerate(cmc_labels):
        mana_curve.append(
            st.slider(
                label, 
                0, 25, curve_preset[i],
                key=f"cmc_{i}"
            )
        )
    
    # Section 4: Deck Composition (Vertical Layout)
    st.header("Deck Composition")
    
    if preset_name != "Custom":
        comp_preset = preset["card_types"]
    else:
        comp_preset = (28, 12, 20)  # DNT default
    
    creature_slider = st.slider(
        "Number of Creatures", 
        0, 60, comp_preset[0],
        key='creatures'
    )
    noncreature_slider = st.slider(
        "Number of Noncreature Spells", 
        0, 60, comp_preset[1],
        key='noncreatures'
    )
    land_slider = st.slider(
        "Number of Lands", 
        0, 60, comp_preset[2],
        key='lands'
    )
    card_types = (creature_slider, noncreature_slider, land_slider)
    
    # Section 5: Algorithm Weight Configuration (Compact)
    st.header("Algorithm Weights")
    
    if preset_name != "Custom":
        weight_preset = preset["weights"]
    else:
        weight_preset = (1.0, 1.0, 1.0, 1.0)  # Default
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cost_eff_weight = st.slider(
            "Cost Effectiveness", 
            0.0, 2.0, weight_preset[0], 0.1,
            key='weight_cost'
        )
    with col2:
        synergy_weight = st.slider(
            "Synergy", 
            0.0, 2.0, weight_preset[1], 0.1,
            key='weight_synergy'
        )
    with col3:
        curve_weight = st.slider(
            "Mana Curve", 
            0.0, 2.0, weight_preset[2], 0.1,
            key='weight_curve'
        )
    with col4:
        strategy_weight = st.slider(
            "Card Types", 
            0.0, 2.0, weight_preset[3], 0.1,
            key='weight_strategy'
        )
    weights = (cost_eff_weight, synergy_weight, curve_weight, strategy_weight)
    
    # Section 6: Generate Deck
    if st.button("Generate Deck", key="generatedeck") and starting_cards:
        if starting_cards == "":
            st.error("Please provide at least one valid starting card")
        # Get legal cards
        legal_cards = {
            c for c in all_cards
            if c.legalities.get("modern") == "legal" 
            and is_nonland(c)
            and is_in_color(c, color_symbols)
        }
        
        if not legal_cards:
            st.error("No legal cards found for selected colors")
            return
            
        # Format parameters
        deck_size_text = f"{card_types[0] + card_types[1]} nonlands + {card_types[2]} lands"
        curve_text = ", ".join(f"{cost}: {count}" for cost, count in enumerate(mana_curve) if count > 0)
        st.info(f"Generating deck: {deck_size_text}, Curve: [{curve_text}], Colors: {color_symbols}")
        
        # Generate deck with stdout capture
        with st.spinner("Generating deck (this may take several minutes)..."):
            try:
                # Capture stdout during generation
                with capture_stdout() as captured:
                    deck = generate_deck(
                        starting_cards,
                        legal_cards,
                        mana_curve,
                        card_types,
                        weights
                    )
                
                # Get captured output
                capture_output = captured.getvalue()
                
                # Display results
                st.success("Deck generated successfully!")
                st.subheader("Deck List")
                
                nonlands = [c for c in deck if is_nonland(c)]
                lands = [c for c in deck if not is_nonland(c)]
                
                st.subheader(f"Nonland Cards ({len(nonlands)})")
                nonland_counts = Counter(card.name for card in nonlands)
                for name, count in nonland_counts.most_common():
                    st.write(f"{count}x {name}")
                
                st.subheader(f"Lands ({len(lands)})")
                st.info("Lands are automatically calculated based on your color selection")
                
                # Display captured output in expander
                with st.expander("Generation Details", expanded=False):
                    st.text_area(
                        "Standard Output",
                        value=capture_output,
                        height=400,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                
            except Exception as e:
                st.error(f"Generation failed: {e}")

if __name__ == "__main__":
    main()
