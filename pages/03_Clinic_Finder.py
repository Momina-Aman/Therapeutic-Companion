"""
Clinic Finder Page - Phase 3 with Folium Integration.

This page integrates interactive Folium maps to help users locate mental health services.

Features:
- Interactive map with clinic markers
- Search by location, service type, and insurance
- Distance-based filtering with Haversine calculation
- Detailed clinic information popups
- Crisis resources and therapeutic modalities guide

Page: 03_Clinic_Finder.py
Module: Therapeutic Companion - Phase 3
"""

import streamlit as st
from auth import check_auth
from pathlib import Path

try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

try:
    from clinics_data import (
        CLINICS_DATA,
        get_clinics_near_location,
        get_clinics_by_type,
        get_clinics_by_specialization
    )
    CLINICS_DATA_AVAILABLE = True
except ImportError:
    CLINICS_DATA_AVAILABLE = False

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Clinic Finder - Therapeutic Companion",
    page_icon="🏥",
    layout="wide"
)

# Check authentication
if not check_auth(st.session_state):
    st.error("Please log in to access this feature.")
    st.stop()


# ============================================================================
# UTILITIES
# ============================================================================

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth (in miles).
    """
    from math import radians, cos, sin, asin, sqrt

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 3959  # Radius of Earth in miles
    return c * r


def get_marker_color(clinic_type):
    """Get color for marker based on clinic type."""
    color_map = {
        "Clinic": "blue",
        "Therapist": "green",
        "Psychiatry": "red",
        "Crisis": "darkred",
        "Telehealth": "purple",
        "Support Group": "orange"
    }
    return color_map.get(clinic_type, "blue")


def render_clinic_markers_on_map(clinics, center_lat, center_lon):
    """Create and render a Folium map with clinic markers."""
    if not FOLIUM_AVAILABLE:
        st.error("Folium not available. Please install: pip install folium streamlit-folium")
        return None

    try:
        # Create map centered on user location
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles="OpenStreetMap"
        )

        # Add user location marker
        folium.Marker(
            location=[center_lat, center_lon],
            popup="Your Location",
            icon=folium.Icon(color="gray", icon="info-sign"),
            tooltip="Your location"
        ).add_to(m)

        # Add clinic markers
        for clinic in clinics:
            marker_color = get_marker_color(clinic.get("type", "Clinic"))

            popup_text = f"""
            <b>{clinic['name']}</b><br>
            <b>Type:</b> {clinic['type']}<br>
            <b>Phone:</b> {clinic['phone']}<br>
            <b>Email:</b> {clinic['email']}<br>
            <b>Website:</b> <a href="{clinic['website']}" target="_blank">Visit</a><br>
            <b>Specializations:</b> {', '.join(clinic['specializations'][:3])}<br>
            <b>Insurance:</b> {', '.join(clinic['insurance'])}
            """

            folium.Marker(
                location=[clinic["latitude"], clinic["longitude"]],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=marker_color, icon="hospital-o"),
                tooltip=clinic['name']
            ).add_to(m)

        return m

    except Exception as e:
        st.error(f"Error creating map: {e}")
        return None


# ============================================================================
# SEARCH INTERFACE WITH MAP
# ============================================================================

def render_search_interface():
    """Render the clinic search interface with map integration."""
    st.subheader("🔍 Search for Mental Health Services")

    if not CLINICS_DATA_AVAILABLE:
        st.warning(
            "⚠️ Clinic data not available. Please ensure clinics_data.py is in the project root."
        )
        return

    col1, col2 = st.columns(2)

    with col1:
        # Location input - using NYC as default center for demo
        location_input = st.text_input(
            "Enter your city:",
            value="New York, NY",
            placeholder="e.g., New York, Los Angeles",
            key="clinic_city"
        )

        service_type = st.selectbox(
            "Type of service:",
            [
                "All Services",
                "Therapist",
                "Psychiatry",
                "Clinic",
                "Crisis",
                "Telehealth",
                "Support Group"
            ],
            key="clinic_service"
        )

    with col2:
        insurance = st.selectbox(
            "Insurance accepted:",
            [
                "Any",
                "Private",
                "Medicare",
                "Medicaid",
                "Sliding Scale"
            ],
            key="clinic_insurance"
        )

        distance_radius = st.slider(
            "Search radius (miles):",
            min_value=1,
            max_value=50,
            value=15,
            step=1,
            key="clinic_distance"
        )

    st.markdown("---")

    if st.button("🗺️ Search Clinics & View Map", use_container_width=True, type="primary"):
        # For demo, use NYC coordinates (40.7128, -74.0060)
        center_lat, center_lon = 40.7128, -74.0060

        # Filter clinics
        filtered_clinics = CLINICS_DATA.copy()

        # Filter by type
        if service_type != "All Services":
            filtered_clinics = [
                c for c in filtered_clinics
                if service_type.lower() in c["type"].lower()
            ]

        # Filter by distance
        if distance_radius:
            nearby_clinics = []
            for clinic in filtered_clinics:
                dist = haversine_distance(
                    center_lat, center_lon,
                    clinic["latitude"], clinic["longitude"]
                )
                if dist <= distance_radius:
                    clinic["distance_miles"] = round(dist, 1)
                    nearby_clinics.append(clinic)
            filtered_clinics = nearby_clinics

        # Filter by insurance
        if insurance != "Any":
            filtered_clinics = [
                c for c in filtered_clinics
                if any(
                    insurance.lower() in ins.lower()
                    for ins in c["insurance"]
                )
            ]

        if filtered_clinics:
            # Display results summary
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.metric("Clinics Found", len(filtered_clinics))
            with col2:
                st.metric("Service Type", service_type)
            with col3:
                st.metric("Search Radius", f"{distance_radius} mi")

            st.markdown("---")

            # Display map
            st.subheader("📍 Clinic Locations Map")
            map_obj = render_clinic_markers_on_map(
                filtered_clinics, center_lat, center_lon
            )

            if map_obj:
                st_folium(map_obj, width=1400, height=500)

            st.markdown("---")

            # Display clinic list
            st.subheader("📋 Clinic Details")

            # Sort by distance if available
            if "distance_miles" in filtered_clinics[0]:
                filtered_clinics.sort(key=lambda x: x.get("distance_miles", 999))

            for idx, clinic in enumerate(filtered_clinics, 1):
                with st.expander(
                    f"{'🩺' if clinic['type'] == 'Psychiatry' else '💬'} "
                    f"{clinic['name']} "
                    f"({clinic['type']}) "
                    f"- {clinic.get('distance_miles', 'N/A')} miles away"
                ):
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.markdown(f"**Phone:** {clinic['phone']}")
                        st.markdown(f"**Email:** {clinic['email']}")
                        st.markdown(
                            f"**Website:** [Visit]({clinic['website']})"
                        )

                    with col2:
                        st.markdown(f"**Type:** {clinic['type']}")
                        st.markdown(f"**Distance:** {clinic.get('distance_miles', 'N/A')} miles")

                    st.write("**Specializations:**")
                    specialization_cols = st.columns(len(clinic["specializations"]))
                    for col, spec in zip(
                        specialization_cols, clinic["specializations"]
                    ):
                        with col:
                            st.write(f"• {spec}")

                    st.write("**Insurance Accepted:**")
                    insurance_cols = st.columns(len(clinic["insurance"]))
                    for col, ins in zip(insurance_cols, clinic["insurance"]):
                        with col:
                            st.write(f"✓ {ins}")

                    st.markdown("---")

                    # Call button
                    if st.button(f"📞 Call {clinic['name']}", key=f"call_{idx}"):
                        st.success(f"Opening phone dialer for {clinic['phone']}")

        else:
            st.warning(
                "No clinics found matching your criteria. "
                "Try adjusting your filters or increasing the search radius."
            )


# ============================================================================
# TIPS & RESOURCES
# ============================================================================

def render_clinic_tips():
    """Render tips for finding a therapist."""
    st.subheader("💡 Tips for Finding a Mental Health Professional")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            ### Research & Verify
            - ✅ Verify credentials and licenses
            - ✅ Check specializations and experience
            - ✅ Read reviews and testimonials
            - ✅ Confirm insurance acceptance
            """
        )

    with col2:
        st.markdown(
            """
            ### Initial Consultation
            - 💬 Many therapists offer free consultations
            - 💬 Ask about their therapeutic approach
            - 💬 Discuss treatment goals and timeline
            - 💬 Ask about fees and payment options
            """
        )


def render_crisis_resources():
    """Render crisis support resources."""
    st.markdown("---")
    st.subheader("🆘 Crisis Support Resources")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            ### United States
            **988 Suicide & Crisis Lifeline**
            - Call or text: **988**
            - Available 24/7
            - Free and confidential
            """
        )

    with col2:
        st.markdown(
            """
            ### International
            **Find Your Local Resource**
            - findahelpline.com
            - befrienders.org
            - Crisis Text Line: Text HOME to 741741
            """
        )

    with col3:
        st.markdown(
            """
            ### Emergency
            **If you're in immediate danger:**
            - Call 911 (US)
            - Go to nearest ER
            - Contact local emergency services
            """
        )


def render_modalities_guide():
    """Render guide to different therapeutic modalities."""
    st.markdown("---")
    st.subheader("📚 Understanding Therapeutic Modalities")

    modalities = {
        "Cognitive Behavioral Therapy (CBT)": {
            "description": "Focuses on changing negative thought patterns and behaviors",
            "best_for": "Anxiety, depression, OCD, PTSD"
        },
        "Dialectical Behavior Therapy (DBT)": {
            "description": "Combines CBT with acceptance and mindfulness techniques",
            "best_for": "Borderline personality disorder, self-harm, chronic suicidality"
        },
        "Psychodynamic Therapy": {
            "description": "Explores unconscious patterns and past experiences",
            "best_for": "Relationship issues, trauma, self-esteem"
        },
        "Humanistic/Person-Centered Therapy": {
            "description": "Emphasizes personal growth and self-actualization",
            "best_for": "General wellbeing, personal growth, existential concerns"
        },
        "Mindfulness-Based Therapy": {
            "description": "Integrates meditation and mindfulness practices",
            "best_for": "Stress, anxiety, chronic pain, relapse prevention"
        },
        "Acceptance & Commitment Therapy (ACT)": {
            "description": "Focus on accepting difficult thoughts while pursuing valued actions",
            "best_for": "Chronic pain, anxiety, depression, trauma"
        }
    }

    for modality, details in modalities.items():
        with st.expander(f"✨ {modality}"):
            st.markdown(f"**Description:** {details['description']}")
            st.markdown(f"**Often Helpful For:** {details['best_for']}")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Render the Clinic Finder page."""
    st.title("🏥 Find Mental Health Services")

    st.markdown("---")

    st.markdown(
        """
        Finding the right mental health professional is an important step in your wellness journey.
        This tool helps you locate therapists, counselors, psychiatrists, and mental health clinics near you.
        """
    )

    st.markdown("---")

    # Check if required modules are available
    if not FOLIUM_AVAILABLE:
        st.warning(
            "📍 **Map feature requires Folium and streamlit-folium**\n\n"
            "Install with: `pip install folium streamlit-folium`\n\n"
            "You can still browse clinics and tips below."
        )

    if not CLINICS_DATA_AVAILABLE:
        st.warning(
            "📍 **Clinic database not found**\n\n"
            "Ensure clinics_data.py exists in the project root."
        )

    render_search_interface()

    render_clinic_tips()

    render_modalities_guide()

    render_crisis_resources()

    st.markdown("---")

    st.success(
        "💙 **Remember**: Seeking help is a sign of strength, not weakness. "
        "You deserve professional support for your mental health."
    )


if __name__ == "__main__":
    main()
