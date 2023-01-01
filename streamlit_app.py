# basic imports
import asyncio
import streamlit as st
import pandas as pd

# imports for search console libraries
import searchconsole
from apiclient import discovery
from google_auth_oauthlib.flow import Flow


# all other imports
import os
from streamlit_elements import Elements

# The code below is for the layout of the page
if "widen" not in st.session_state:
    layout = "centered"
else:
    layout = "wide" if st.session_state.widen else "centered"

st.set_page_config(
    layout=layout, page_title="CTR - Google Search Console Connector", page_icon="🔌"
)

# row limit
#RowCap = 25000
RowCap =  st.slider('Nombre de résultats API à récupérer',10, 100000,25000)

st.sidebar.image("logo.png", width=290)

st.sidebar.markdown("")

st.write("")

# Convert secrets from the TOML file to strings
clientSecret = str(st.secrets["installed"]["client_secret"])
clientId = str(st.secrets["installed"]["client_id"])
redirectUri = str(st.secrets["installed"]["redirect_uris"][0])

st.markdown("")

if "my_token_input" not in st.session_state:
    st.session_state["my_token_input"] = ""

if "my_token_received" not in st.session_state:
    st.session_state["my_token_received"] = False

def charly_form_callback():
    # st.write(st.session_state.my_token_input)
    st.session_state.my_token_received = True
    code = st.experimental_get_query_params()["code"][0]
    st.session_state.my_token_input = code

with st.sidebar.form(key="my_form"):

    st.markdown("")

    mt = Elements()

    mt.button(
        "Sign-in with Google",
        target="_blank",
        size="large",
        variant="contained",
        start_icon=mt.icons.exit_to_app,
        onclick="none",
        style={"color": "#FFFFFF", "background": "#FF4B4B"},
        href="https://accounts.google.com/o/oauth2/auth?response_type=code&client_id="
        + clientId
        + "&redirect_uri="
        + redirectUri
        + "&scope=https://www.googleapis.com/auth/webmasters.readonly&access_type=offline&prompt=consent",
    )

    mt.show(key="687")

    credentials = {
        "installed": {
            "client_id": clientId,
            "client_secret": clientSecret,
            "redirect_uris": [],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
        }
    }

    flow = Flow.from_client_config(
        credentials,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        redirect_uri=redirectUri,
    )

    auth_url, _ = flow.authorization_url(prompt="consent")

    submit_button = st.form_submit_button(
        label="Access GSC API", on_click=charly_form_callback
    )

    st.write("")

    with st.expander("How to access your GSC data?"):
        st.markdown(
            """
        1. Click on the `Sign-in with Google` button
        2. You will be redirected to the Google Oauth screen
        3. Choose the Google account you want to use & click `Continue`
        5. You will be redirected back to this app.
        6. Click on the "Access GSC API" button.
        7. Voilà! 🙌 
        """
        )
        st.write("")

    with st.expander("Check your Oauth token"):
        code = st.text_input(
            "",
            key="my_token_input",
            label_visibility="collapsed",
        )

    st.write("")

container3 = st.sidebar.container()

st.sidebar.write("")

st.sidebar.caption(
    "Made in 🎈 [Streamlit](https://www.streamlit.io/), by [Charly Wargnier](https://www.charlywargnier.com/)."
)

try:

    if st.session_state.my_token_received == False:

        with st.form(key="my_form2"):

            # text_input_container = st.empty()
            webpropertiesNEW = st.text_input(
                "Web property to review (please sign in via Google OAuth first)",
                value="",
                disabled=True,
            )

            filename = webpropertiesNEW.replace("https://www.", "")
            filename = filename.replace("http://www.", "")
            filename = filename.replace(".", "")
            filename = filename.replace("/", "")

            col1, col2, col3 = st.columns(3)

            with col1:
                dimension = st.selectbox(
                    "Dimension",
                    (
                        "query",
                        "page",
                        "date",
                        "device",
                        "searchAppearance",
                        "country",
                    ),
                    help="Choose a top dimension",
                )

            with col2:
                nested_dimension = st.selectbox(
                    "Nested dimension",
                    (
                        "none",
                        "query",
                        "page",
                        "date",
                        "device",
                        "searchAppearance",
                        "country",
                    ),
                    help="Choose a nested dimension",
                )

            with col3:
                nested_dimension_2 = st.selectbox(
                    "Nested dimension 2",
                    (
                        "none",
                        "query",
                        "page",
                        "date",
                        "device",
                        "searchAppearance",
                        "country",
                    ),
                    help="Choose a second nested dimension",
                )

            st.write("")

            col1, col2 = st.columns(2)

            with col1:
                search_type = st.selectbox(
                    "Search type",
                    ("web", "video", "image", "news", "googleNews"),
                    help="""
                    Specify the search type you want to retrieve
                    -   **Web**: Results that appear in the All tab. This includes any image or video results shown in the All results tab.
                    -   **Image**: Results that appear in the Images search results tab.
                    -   **Video**: Results that appear in the Videos search results tab.
                    -   **News**: Results that show in the News search results tab.

                    """,
                )

            with col2:
                timescale = st.selectbox(
                    "Date range",
                    (
                        "Last 7 days",
                        "Last 30 days",
                        "Last 3 months",
                        "Last 6 months",
                        "Last 12 months",
                        "Last 16 months",
                    ),
                    index=0,
                    help="Specify the date range",
                )

                if timescale == "Last 7 days":
                    timescale = -7
                elif timescale == "Last 30 days":
                    timescale = -30
                elif timescale == "Last 3 months":
                    timescale = -91
                elif timescale == "Last 6 months":
                    timescale = -182
                elif timescale == "Last 12 months":
                    timescale = -365
                elif timescale == "Last 16 months":
                    timescale = -486

            st.write("")

            with st.expander("✨ Advanced Filters", expanded=False):

                col1, col2, col3 = st.columns(3)

                with col1:
                    filter_page_or_query = st.selectbox(
                        "Dimension to filter #1",
                        ("query", "page", "device", "searchAppearance", "country"),
                        help="""
                        You can choose to filter dimensions and apply filters before executing a query.
                        """,
                    )

                with col2:
                    filter_type = st.selectbox(
                        "Filter type",
                        (
                            "contains",
                            "equals",
                            "notContains",
                            "notEquals",
                            "includingRegex",
                            "excludingRegex",
                        ),
                        help="""
                        Note that if you use Regex in your filter, you must follow the `RE2` syntax.
                        """,
                    )

                with col3:
                    filter_keyword = st.text_input(
                        "Keyword(s) to filter ",
                        "",
                        help="Add the keyword(s) you want to filter",
                    )

                with col1:
                    filter_page_or_query2 = st.selectbox(
                        "Dimension to filter #2",
                        ("query", "page", "device", "searchAppearance", "country"),
                        key="filter_page_or_query2",
                        help="""
                        You can choose to filter dimensions and apply filters before executing a query.
                        """,
                    )

                with col2:
                    filter_type2 = st.selectbox(
                        "Filter type",
                        (
                            "contains",
                            "equals",
                            "notContains",
                            "notEquals",
                            "includingRegex",
                            "excludingRegex",
                        ),
                        key="filter_type2",
                        help="""
                        Note that if you use Regex in your filter, you must follow the `RE2` syntax.
                        """,
                    )

                with col3:
                    filter_keyword2 = st.text_input(
                        "Keyword(s) to filter ",
                        "",
                        key="filter_keyword2",
                        help="Add the keyword(s) you want to filter",
                    )

                with col1:
                    filter_page_or_query3 = st.selectbox(
                        "Dimension to filter #3",
                        ("query", "page", "device", "searchAppearance", "country"),
                        key="filter_page_or_query3",
                        help="""
                        You can choose to filter dimensions and apply filters before executing a query.
                        """,
                    )

                with col2:
                    filter_type3 = st.selectbox(
                        "Filter type",
                        (
                            "contains",
                            "equals",
                            "notContains",
                            "notEquals",
                            "includingRegex",
                            "excludingRegex",
                        ),
                        key="filter_type3",
                        help="""
                        Note that if you use Regex in your filter, you must follow the `RE2` syntax.
                        """,
                    )

                with col3:
                    filter_keyword3 = st.text_input(
                        "Keyword(s) to filter ",
                        "",
                        key="filter_keyword3",
                        help="Add the keyword(s) you want to filter",
                    )

                st.write("")

            submit_button = st.form_submit_button(
                label="Fetch GSC API data", on_click=charly_form_callback
            )

        if (nested_dimension != "none") and (nested_dimension_2 != "none"):

            if (
                (dimension == nested_dimension)
                or (dimension == nested_dimension_2)
                or (nested_dimension == nested_dimension_2)
            ):
                st.warning(
                    "🚨 Dimension and nested dimensions cannot be the same, please make sure you choose unique dimensions."
                )
                st.stop()

            else:
                pass

        elif (nested_dimension != "none") and (nested_dimension_2 == "none"):
            if dimension == nested_dimension:
                st.warning(
                    "🚨 Dimension and nested dimensions cannot be the same, please make sure you choose unique dimensions."
                )
                st.stop()
            else:
                pass

        else:
            pass

    if st.session_state.my_token_received == True:

        @st.experimental_singleton
        def get_account_site_list_and_webproperty(token):
            flow.fetch_token(code=token)
            credentials = flow.credentials
            service = discovery.build(
                serviceName="webmasters",
                version="v3",
                credentials=credentials,
                cache_discovery=False,
            )

            account = searchconsole.account.Account(service, credentials)
            site_list = service.sites().list().execute()
            return account, site_list

        account, site_list = get_account_site_list_and_webproperty(
            st.session_state.my_token_input
        )

        first_value = list(site_list.values())[0]

        lst = []
        for dicts in first_value:
            a = dicts.get("siteUrl")
            lst.append(a)

        if lst:

            container3.info("✔️ GSC credentials OK!")

            with st.form(key="my_form2"):

                webpropertiesNEW = st.selectbox("Select web property", lst)

                col1, col2, col3 = st.columns(3)

                with col1:
                    dimension = st.selectbox(
                        "Dimension",
                        (
                            "query",
                            "page",
                            "date",
                            "device",
                            "searchAppearance",
                            "country",
                        ),
                        help="Choose your top dimension",
                    )

                with col2:
                    nested_dimension = st.selectbox(
                        "Nested dimension",
                        (
                            "none",
                            "query",
                            "page",
                            "date",
                            "device",
                            "searchAppearance",
                            "country",
                        ),
                        help="Choose a nested dimension",
                    )

                with col3:
                    nested_dimension_2 = st.selectbox(
                        "Nested dimension 2",
                        (
                            "none",
                            "query",
                            "page",
                            "date",
                            "device",
                            "searchAppearance",
                            "country",
                        ),
                        help="Choose a second nested dimension",
                    )

                st.write("")

                col1, col2 = st.columns(2)

                with col1:
                    search_type = st.selectbox(
                        "Search type",
                        ("web", "news", "video", "googleNews", "image"),
                        help="""
                    Specify the search type you want to retrieve
                    -   **Web**: Results that appear in the All tab. This includes any image or video results shown in the All results tab.
                    -   **Image**: Results that appear in the Images search results tab.
                    -   **Video**: Results that appear in the Videos search results tab.
                    -   **News**: Results that show in the News search results tab.

                    """,
                    )

                with col2:
                    timescale = st.selectbox(
                        "Date range",
                        (
                            "Last 7 days",
                            "Last 30 days",
                            "Last 3 months",
                            "Last 6 months",
                            "Last 12 months",
                            "Last 16 months",
                        ),
                        index=0,
                        help="Specify the date range",
                    )

                    if timescale == "Last 7 days":
                        timescale = -7
                    elif timescale == "Last 30 days":
                        timescale = -30
                    elif timescale == "Last 3 months":
                        timescale = -91
                    elif timescale == "Last 6 months":
                        timescale = -182
                    elif timescale == "Last 12 months":
                        timescale = -365
                    elif timescale == "Last 16 months":
                        timescale = -486

                st.write("")

                with st.expander("✨ Advanced Filters", expanded=False):

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        filter_page_or_query = st.selectbox(
                            "Dimension to filter #1",
                            (
                                "query",
                                "page",
                                "device",
                                "searchAppearance",
                                "country",
                            ),
                            help="You can choose to filter dimensions and apply filters before executing a query.",
                        )

                    with col2:
                        filter_type = st.selectbox(
                            "Filter type",
                            (
                                "contains",
                                "equals",
                                "notContains",
                                "notEquals",
                                "includingRegex",
                                "excludingRegex",
                            ),
                            help="Note that if you use Regex in your filter, you must follow `RE2` syntax.",
                        )

                    with col3:
                        filter_keyword = st.text_input(
                            "Keyword(s) to filter ",
                            "",
                            help="Add the keyword(s) you want to filter",
                        )

                    with col1:
                        filter_page_or_query2 = st.selectbox(
                            "Dimension to filter #2",
                            (
                                "query",
                                "page",
                                "device",
                                "searchAppearance",
                                "country",
                            ),
                            key="filter_page_or_query2",
                            help="You can choose to filter dimensions and apply filters before executing a query.",
                        )

                    with col2:
                        filter_type2 = st.selectbox(
                            "Filter type",
                            (
                                "contains",
                                "equals",
                                "notContains",
                                "notEquals",
                                "includingRegex",
                                "excludingRegex",
                            ),
                            key="filter_type2",
                            help="Note that if you use Regex in your filter, you must follow `RE2` syntax.",
                        )

                    with col3:
                        filter_keyword2 = st.text_input(
                            "Keyword(s) to filter ",
                            "",
                            key="filter_keyword2",
                            help="Add the keyword(s) you want to filter",
                        )

                    with col1:
                        filter_page_or_query3 = st.selectbox(
                            "Dimension to filter #3",
                            (
                                "query",
                                "page",
                                "device",
                                "searchAppearance",
                                "country",
                            ),
                            key="filter_page_or_query3",
                            help="You can choose to filter dimensions and apply filters before executing a query.",
                        )

                    with col2:
                        filter_type3 = st.selectbox(
                            "Filter type",
                            (
                                "contains",
                                "equals",
                                "notContains",
                                "notEquals",
                                "includingRegex",
                                "excludingRegex",
                            ),
                            key="filter_type3",
                            help="Note that if you use Regex in your filter, you must follow `RE2` syntax.",
                        )

                    with col3:
                        filter_keyword3 = st.text_input(
                            "Keyword(s) to filter ",
                            "",
                            key="filter_keyword3",
                            help="Add the keyword(s) you want to filter",
                        )

                    st.write("")

                submit_button = st.form_submit_button(
                    label="Fetch GSC API data", on_click=charly_form_callback
                )

            if (nested_dimension != "none") and (nested_dimension_2 != "none"):

                if (
                    (dimension == nested_dimension)
                    or (dimension == nested_dimension_2)
                    or (nested_dimension == nested_dimension_2)
                ):
                    st.warning(
                        "🚨 Dimension and nested dimensions cannot be the same, please make sure you choose unique dimensions."
                    )
                    st.stop()

                else:
                    pass

            elif (nested_dimension != "none") and (nested_dimension_2 == "none"):
                if dimension == nested_dimension:
                    st.warning(
                        "🚨 Dimension and nested dimensions cannot be the same, please make sure you choose unique dimensions."
                    )
                    st.stop()
                else:
                    pass

            else:
                pass

        def get_search_console_data(webproperty):
            if webproperty is not None:
                report = (
                    webproperty.query.search_type(search_type)
                    .range("today", days=timescale)
                    .dimension(dimension)
                    .filter(filter_page_or_query, filter_keyword, filter_type)
                    .filter(filter_page_or_query2, filter_keyword2, filter_type2)
                    .filter(filter_page_or_query3, filter_keyword3, filter_type3)
                    .limit(RowCap)
                    .get()
                    .to_dataframe()
                )
                return report
            else:
                st.warning("No webproperty found")
                st.stop()

        def get_search_console_data_nested(webproperty):
            if webproperty is not None:
                # query = webproperty.query.range(start="today", days=days).dimension("query")
                report = (
                    webproperty.query.search_type(search_type)
                    .range("today", days=timescale)
                    .dimension(dimension, nested_dimension)
                    .filter(filter_page_or_query, filter_keyword, filter_type)
                    .filter(filter_page_or_query2, filter_keyword2, filter_type2)
                    .filter(filter_page_or_query3, filter_keyword3, filter_type3)
                    .limit(RowCap)
                    .get()
                    .to_dataframe()
                )
                return report

        def get_search_console_data_nested_2(webproperty):
            if webproperty is not None:
                # query = webproperty.query.range(start="today", days=days).dimension("query")
                report = (
                    webproperty.query.search_type(search_type)
                    .range("today", days=timescale)
                    .dimension(dimension, nested_dimension, nested_dimension_2)
                    .filter(filter_page_or_query, filter_keyword, filter_type)
                    .filter(filter_page_or_query2, filter_keyword2, filter_type2)
                    .filter(filter_page_or_query3, filter_keyword3, filter_type3)
                    .limit(RowCap)
                    .get()
                    .to_dataframe()
                )
                return report

        # Here are some conditions to check which function to call

        if nested_dimension == "none" and nested_dimension_2 == "none":

            webproperty = account[webpropertiesNEW]

            df = get_search_console_data(webproperty)

            if df.empty:
                st.warning(
                    "🚨 There's no data for your selection, please refine your search with different criteria"
                )
                st.stop()

        elif nested_dimension_2 == "none":

            webproperty = account[webpropertiesNEW]

            df = get_search_console_data_nested(webproperty)

            if df.empty:
                st.warning(
                    "🚨 DataFrame is empty! Please refine your search with different criteria"
                )
                st.stop()

        else:

            webproperty = account[webpropertiesNEW]

            df = get_search_console_data_nested_2(webproperty)

            if df.empty:
                st.warning(
                    "🚨 DataFrame is empty! Please refine your search with different criteria"
                )
                st.stop()

        st.write(
            "##### # of results returned by API call: ",
            len(df.index),
        )

        # Initialisation du dictionnaire avec les tranches de position comme clés et 0 comme valeur
        ctr_by_position = {
            "1": 0,
            "1->2": 0,
            "2->3": 0,
            "3->4": 0,
            "4->5": 0,
            "5->6": 0,
            "6->7": 0,
            "7->8": 0,
            "8->9": 0,
            "9->10": 0,
            "10 et +": 0
        }
        clics_by_position = {
            "1": 0,
            "1->2": 0,
            "2->3": 0,
            "3->4": 0,
            "4->5": 0,
            "5->6": 0,
            "6->7": 0,
            "7->8": 0,
            "8->9": 0,
            "9->10": 0,
            "10 et +": 0
        }
        impressions_by_position = {
            "1": 0,
            "1->2": 0,
            "2->3": 0,
            "3->4": 0,
            "4->5": 0,
            "5->6": 0,
            "6->7": 0,
            "7->8": 0,
            "8->9": 0,
            "9->10": 0,
            "10 et +": 0
        }
        queries_by_position = {
            "1": 0,
            "1->2": 0,
            "2->3": 0,
            "3->4": 0,
            "4->5": 0,
            "5->6": 0,
            "6->7": 0,
            "7->8": 0,
            "8->9": 0,
            "9->10": 0,
            "10 et +": 0
        }
        query_by_position = {
            "0->1": 0,
            "1->2": 0,
            "2->3": 0,
            "3->4": 0,
            "4->5": 0,
            "5->6": 0,
            "6->7": 0,
            "7->8": 0,
            "8->9": 0,
            "9->10": 0,
            "10 et +": 0
        }

        nb_rows = 0

        max_impressions_found = 0
        max_clics_found = 0

        @st.cache
        def convert_df(df):
            return df.to_csv().encode("utf-8")

        csv = convert_df(df)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="large_df.csv",
            mime="text/csv",
        )
        
        for index, row in df.iterrows():
            #st.write(row['query'], row['clicks'])
            if(int(row['impressions'])>max_impressions_found):
                max_impressions_found = int(row['impressions'])
            if(int(row['clicks'])>max_clics_found):
                max_clics_found = int(row['clicks'])

        slider_clic = st.slider('Nombre de clics minimum par mot clé à analyser', 0, 100)
        slider_max_clics = st.slider('Nombre de clics maximum par mot clé à analyser', 0, max_clics_found,max_clics_found)

        slider_max_impressions = st.slider('Nombre d\'impressions maximum par mot clé à analyser', 0, max_impressions_found,max_impressions_found)

        #st.bar_chart(df)
        for index, row in df.iterrows():
            if row['impressions']:
                position = float(row['position'])
                clics = int(row['clicks'])
                impressions = int(row['impressions'])
                if(int(row['clicks']) > slider_clic and int(row['clicks']) < slider_max_clics \
                    and int(row['impressions']) < slider_max_impressions):
                    if position == 1:
                        clics_by_position["1"]       += clics
                        impressions_by_position["1"] += impressions
                        queries_by_position["1"]     += 1
                    elif 1 <= position <= 2:
                        clics_by_position["1->2"]       += clics
                        impressions_by_position["1->2"] += impressions
                        queries_by_position["1->2"]     += 1
                    elif 2 < position <= 3:
                        clics_by_position["2->3"]       += clics
                        impressions_by_position["2->3"] += impressions
                        queries_by_position["2->3"]     += 1
                    elif 3 < position <= 4:
                        clics_by_position["3->4"]       += clics
                        impressions_by_position["3->4"] += impressions
                        queries_by_position["3->4"]     += 1
                    elif 4 < position <= 5:
                        clics_by_position["4->5"]       += clics
                        impressions_by_position["4->5"] += impressions
                        queries_by_position["4->5"]     += 1
                    elif 5 < position <= 6:
                        clics_by_position["5->6"]       += clics
                        impressions_by_position["5->6"] += impressions
                        queries_by_position["5->6"]     += 1
                    elif 6 < position <= 7:
                        clics_by_position["6->7"]       += clics
                        impressions_by_position["6->7"] += impressions
                        queries_by_position["6->7"]     += 1
                    elif 7 < position <= 8:
                        clics_by_position["7->8"]       += clics
                        impressions_by_position["7->8"] += impressions
                        queries_by_position["7->8"]     += 1
                    elif 8 < position <= 9:
                        clics_by_position["8->9"]       += clics
                        impressions_by_position["8->9"] += impressions
                        queries_by_position["8->9"]     += 1
                    elif 9 < position <= 10:
                        clics_by_position["9->10"]       += clics
                        impressions_by_position["9->10"] += impressions
                        queries_by_position["9->10"]     += 1
                    else:
                        clics_by_position["10 et +"]       += clics
                        impressions_by_position["10 et +"] += impressions
                        queries_by_position["9->10"]       += 1
                    # Incrémentation du compteur du nombre de lignes
                    nb_rows += 1

        # Calcul du CTR moyen par tranche de position
        for position, clicks in clics_by_position.items():
            impressions = impressions_by_position[position]
            if(impressions):
                ctr_by_position[position] = round(clicks / impressions*100)
            else:
                ctr_by_position[position] = 0
        #df_ctr_by_position = pd.DataFrame.from_dict(ctr_by_position, orient='index', columns=['CTR par sum total'])


        #Trafic potentiel par requête
        query_analysables = {}
        list_keywords = st.text_area('Liste de mots clés à analyser en priorité')

        list_keywords_splited = list_keywords.split('\n')
        for kw in list_keywords_splited:
            for index, row in df.iterrows():
                diff_trafic = 0
                if(row['query'] in [kw]):
                    position = float(row['position'])
                    clicks = int(row['clicks'])
                    impressions = int(row['impressions'])
                    diff_trafic = round(impressions * ctr_by_position["1->2"] / 100 - clicks)
                    if(position < 2):
                        query_analysables[row['query']] = 0
                    elif diff_trafic < 0:
                        query_analysables[row['query']] = 0
                    else:
                         query_analysables[row['query']] = diff_trafic

        qa = pd.DataFrame(list(query_analysables.items()))
        qa.columns =['Requête','Potentiel Gain trafic ']
        st.dataframe(qa)

        #2e tableau avec toutes les opportunités liées à ce KW
        toutes_requetes = {}
        for index, row in df.iterrows():
            position = float(row['position'])
            clicks = int(row['clicks'])
            impressions = int(row['impressions'])
            diff_trafic = round(impressions * ctr_by_position["1->2"] / 100 - clicks)
            if(position > 2):
                toutes_requetes[row['query']] = diff_trafic
        df_toutes_requetes = pd.DataFrame(list(toutes_requetes.items()))
        df_toutes_requetes.columns =['Requête','Trafic potentiel']
        st.write(ctr_by_position)
        st.dataframe(df_toutes_requetes)

        #CTR par position - Graphique
        st.header("Graphique")
        st.write('Desactivé pour optimiser performance')
        #st.bar_chart(df)

        #CTR par position - Tableau 
        st.header("Data")
        df['query_by_position'] = query_by_position
        st.write('Desactivé pour optimiser performance')
        #st.dataframe(df)



except ValueError as ve:

    st.warning("⚠️ You need to sign in to your Google account first!")

except IndexError:
    st.info(
        "⛔ It seems you haven’t correctly configured Google Search Console! Click [here](https://support.google.com/webmasters/answer/9008080?hl=en) for more information on how to get started!"
    )