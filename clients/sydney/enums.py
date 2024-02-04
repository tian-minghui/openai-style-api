from enum import Enum


class ConversationStyle(Enum):
    """
    Copilot conversation styles. Supported options are:
    - `creative` for original and imaginative chat
    - `balanced` for informative and friendly chat
    - `precise` for concise and straightforward chat
    """

    CREATIVE = "Creative"
    BALANCED = "Balanced"
    PRECISE = "Precise"


class ConversationStyleOptionSets(Enum):
    """
    Copilot conversation styles. Supported options are:
    - `creative` for original and imaginative chat
    - `balanced` for informative and friendly chat
    - `precise` for concise and straightforward chat
    """

    CREATIVE = "h3imaginative,clgalileo,gencontentv3"
    BALANCED = "galileo"
    PRECISE = "h3precise,clgalileo"


class ConversationHistoryOptionsSets(Enum):
    AUTOSAVE = "autosave"
    SAVEMEM = "savemem"
    UPROFUPD = "uprofupd"
    UPROFGEN = "uprofgen"


class DefaultOptions(Enum):
    """
    Options that are used in all API requests to Copilot.
    """

    NLU_DIRECT_RESPONSE_FILTER = "nlu_direct_response_filter"
    DEEPLEO = "deepleo"
    DISABLE_EMOJI_SPOKEN_TEXT = "disable_emoji_spoken_text"
    RESPONSIBLE_AI_POLICY_235 = "responsible_ai_policy_235"
    ENABLEMM = "enablemm"
    DV3SUGG = "dv3sugg"
    IYXAPBING = "iyxapbing"
    IYCAPBING = "iycapbing"
    SAHARAGENCONV5 = "saharagenconv5"
    EREDIRECTURL = "eredirecturl"


class NoSearchOptions(Enum):
    """
    Options that are used to disable search access.
    """

    NOSEARCHALL = "nosearchall"


class DefaultComposeOptions(Enum):
    """
    Options that are used in all compose API requests to Copilot.
    """

    NLU_DIRECT_RESPONSE_FILTER = "nlu_direct_response_filter"
    DEEPLEO = "deepleo"
    ENABLE_DEBUG_COMMANDS = "enable_debug_commands"
    DISABLE_EMOJI_SPOKEN_TEXT = "disable_emoji_spoken_text"
    RESPONSIBLE_AI_POLICY_235 = "responsible_ai_policy_235"
    ENABLEMM = "enablemm"
    SOEDGECA = "soedgeca"
    MAX_TURNS_5 = "max_turns_5"


class CookieOptions(Enum):
    """
    Options that are used only when the user is logged in
    and using cookies to use in requests to Copilot.
    """

    AUTOSAVE = "autosave"


class ComposeTone(Enum):
    """
    Copilot compose tones. Supported options are:
    - `professional` for formal conversations in a professional setting
    - `casual` for informal conversations between friends or family members
    - `enthusiastic` for conversations where the writer wants to convey excitement or passion
    - `informational` for conversations where the writer wants to convey information or knowledge
    - `funny` for conversations where the writer wants to be humorous or entertaining
    """

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    INFORMATIONAL = "informational"
    FUNNY = "funny"


class ComposeFormat(Enum):
    """
    Copilot compose formats. Supported options are:
    - `paragraph` for longer messages that are composed of multiple sentences or paragraphs
    - `email` for messages that are structured like emails, with a clear subject line and formal greeting and closing
    - `blogpost` for messages that are structured like blog posts, with clear headings and subheadings and a more informal tone
    - `ideas` for messages that are used to brainstorm or share ideas
    """

    PARAGRAPH = "paragraph"
    EMAIL = "email"
    BLOGPOST = "blog post"
    IDEAS = "bullet point list"


class ComposeLength(Enum):
    """
    Copilot compose lengths. Supported options are:
    - `short` for messages that are only a few words or sentences long
    - `medium` for messages that are a few paragraphs long
    - `long` for messages that are several paragraphs or pages long
    """

    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class CustomComposeTone:
    """
    Class to represent custom Copilot compose tones.
    """

    def __init__(self, value) -> None:
        self.value = value


class MessageType(Enum):
    """
    Allowed message types.
    """

    CHAT = "Chat"
    ACTION_REQUEST = "ActionRequest"
    ADS_QUERY = "AdsQuery"
    CONFIRMATION_CARD = "ConfirmationCard"
    CONTEXT = "Context"
    DISENGAGED = "Disengaged"
    INTERNAL_LOADER_MESSAGE = "InternalLoaderMessage"
    INTERNAL_SEARCH_QUERY = "InternalSearchQuery"
    INTERNAL_SEARCH_RESULT = "InternalSearchResult"
    INVOKE_ACTION = "InvokeAction"
    PROGRESS = "Progress"
    RENDER_CARD_REQUEST = "RenderCardRequest"
    RENDER_CONTENT_REQUEST = "RenderContentRequest"
    SEMANTIC_SERP = "SemanticSerp"
    GENERATE_CONTENT_QUERY = "GenerateContentQuery"
    SEARCH_QUERY = "SearchQuery"


class ResultValue(Enum):
    """
    Copilot result values on raw responses. Supported options are:
    - `Success`
    - `Throttled`
    - `CaptchaChallenge`
    """

    SUCCESS = "Success"
    THROTTLED = "Throttled"
    CAPTCHA_CHALLENGE = "CaptchaChallenge"
