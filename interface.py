"""Interfaces with the PelotonAPI to leverage Streamlit's caching.

Streamlit cannot directly cache a custom class so these interfaces have
a custom hash function defined for the custom class to allow caching the 
custom class.

https://docs.streamlit.io/develop/concepts/architecture/caching#example-1-hashing-a-custom-class
"""

import streamlit as st
from peloton import PelotonAPI


def hash_func(obj: PelotonAPI) -> str:
    return ""


@st.cache_data(hash_funcs={PelotonAPI: hash_func})
def get_user_workouts(
    obj: PelotonAPI,
    user_id: str,
    page: str = 0
):
    return obj.get_user_workouts(user_id, page)


@st.cache_data(hash_funcs={PelotonAPI: hash_func})
def get_instructor_list(
    obj: PelotonAPI,
):
    return obj.get_instructor_list()


@st.cache_data(hash_funcs={PelotonAPI: hash_func})
def get_available_classes(
    obj: PelotonAPI
):
    return obj.get_recent_classes()
