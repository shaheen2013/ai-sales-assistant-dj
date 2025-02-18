import os
import pandas as pd
import json
from langchain.agents import AgentExecutor
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from utils.inventory.tools.vehicle_item_tools import *
from utils.authentication.tools.contact_tools import (
    CollectContactDetailsTool,
    CheckContactDetailsTool,
    load_contact_details,
)
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages

# from vehicle_item_inventory.vehicle_item_inventory_functions import load_json
from inventory.models import VehicleItemInventory


# Load vehicle item inventory
# INVENTORY_FILE = "../data/dummy_vehicle_item_inventory.csv"
# df_item_inventory = pd.read_csv(INVENTORY_FILE)


# Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"

# 💾 **Dictionary to store conversation memory per user**
conversation_memories = {}


def run_agent_executor(user_input, user_id="default"):
    """Runs the LangChain agent with memory and maintains conversation history."""
    item_inventory_objects = VehicleItemInventory.objects.values(
        "name", "code", "price", "stock_quantity"
    )
    df_item_inventory = pd.DataFrame(item_inventory_objects)

    # Convert inventory to a structured string
    item_inventory_str = df_item_inventory.to_string(index=False)

    if user_id not in conversation_memories:
        conversation_memories[user_id] = ConversationBufferMemory(return_messages=True)

    memory = conversation_memories[user_id]

    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.0, api_key=OPENAI_API_KEY)

    tools = [
        GetItemAvailabilityTool(),
        GetItemPriceTool(),
        GetStockAvailabilityTool(),
        OrderItemTool(),
        # CardDetailsCollectionTool(),
        ProcessPaymentTool(user_id=user_id),
        # GenerateInvoiceTool(),
        CollectContactDetailsTool(user_id=user_id),
        CheckContactDetailsTool(user_id=user_id),
    ]

    # 🔄 **Load Contact Details**
    contact_details = load_contact_details(user_id)

    if contact_details:
        contact_str = (
            f"✅ **Existing Contact Details Found:**\n"
            f"👤 **Name:** {contact_details['first_name']} {contact_details['last_name']}\n"
            f"📧 **Email:** {contact_details['email']}\n"
            f"📞 **Phone:** {contact_details['phone_number']}\n"
            f"🏠 **Street address:** {contact_details['street_address']}\n"
            f"📪 **Zip code:** {contact_details['zip_code']}\n"
            f"🌆 **City:** {contact_details['city']}\n"
            f"🌐 **State:** {contact_details['state']}\n"
        )
        contact_confirmation_message = "I have your existing contact details. Would you like to **confirm or update** them before proceeding?"
    else:
        contact_str = "❌ No contact details found. Please provide your details before proceeding."
        contact_confirmation_message = (
            "I need to collect your contact details before proceeding with your order."
        )

    # 📜 **System Prompt with Inventory**
    system_prompt = f"""
    You are an AI assistant for vehicle item inventory management. You help users find and purchase vehicle parts.
    You have access to the current vehicle item inventory and can help users find vehicle items.
    When the user asks for available items, at first check if sufficient quantities of items are available in the inventory.
    If no items are available for a particular item, inform the user.

    **Here is the current inventory:**
    {item_inventory_str}

    **User Contact Details:**
    {contact_str}

    **Instructions:**
    - If the user asks about an item, fetch its price, stock, or availability.
    - Upper and lower case variations of the item name should be handled. Singular and plural forms should be considered same. For example, "trye" and "tires" should be name as the same as item name based on the inventory.
    - User Item name **must be** mapped with the name field of inventory data. Also handle singular and plural forms and mapped according to the inventory name field.
    - If the user wants to place an order, confirm stock before proceeding. Ask for confirmation from the user.
    - Multiple items can be ordered in a single transaction.
    - If an order is confirmed, always check if **contact details exist**.
    - If details exist, you **must** show the user the available contact details and ask if they want to **confirm or update them**.
    - If details do not exist, request them before proceeding. After collecting details, ask for confirmation.
    - If contact details are confirmed, process payment and show the stripe payment url to user for payment.
    **Ensure that `process_payment` receives an item or a list of items.**
    

    **User Contact Confirmation:**
    {contact_confirmation_message}
    """

    # - **VERY IMPORTANT: When collecting payment details, explicitly mention that the order has been saved and will be processed after payment confirmation.**
    # - **Ensure that `process_payment` receives an item or a list of items.**
    # - **After payment, generate and save an invoice in invoice.json.**
    # - If payment is successful, **deduct the purchased quantities from inventory**.

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    functions = [format_tool_to_openai_function(t) for t in tools]
    llm_with_tools = llm.bind(functions=functions)

    agent = (
        {
            "input": lambda x: x["input"],
            "chat_history": lambda _: memory.load_memory_variables({})["history"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(
                x["intermediate_steps"]
            ),
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    result = agent_executor.invoke({"input": user_input})

    memory.save_context(
        {"input": user_input}, {"output": result.get("output", "No response")}
    )

    return result.get("output", "No response")
