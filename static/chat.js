

const printMessages = (data,userId) => {
    const messageChartContainer = document.getElementById("messagesContainer");
  const isMyMessage = data.sender_id == userId;
  console.log("isMyMessage", isMyMessage, data.sender_id, userId )
  const isServerMessage = data.send_by === "server";

  const MessageItemBlockMain = document.createElement("div");
  MessageItemBlockMain.classList.add(
    "messageItemBlock",
    "flex",
    "items-center",
    "space-x-3",
    "p-2",
    "bg-white",
    "rounded-lg",
    isMyMessage
      ? "my_message"
      : isServerMessage
      ? "server_msg"
      : "other-message"
  );
  const userProfileElement = document.createElement("div");
  userProfileElement.classList.add(
    "w-8",
    "h-8",
    "rounded-full",
    "bg-blue-500",
    "text-white",
    "flex",
    "items-center",
    "justify-center",
    "uppercase"
  );

  userProfileElement.textContent = data.send_by.charAt(0);

  const messageContentWrap = document.createElement("div");
  messageContentWrap.classList.add(
    "bg-blue-100",
    "text-blue-900",
    "rounded-lg",
    "p-3"
  );

  if (isMyMessage && !isServerMessage) {
    userProfileElement.classList.add("bg-green-500");
    messageContentWrap.classList.add("bg-green-100", "text-blue-900");
  }

  const messageText = document.createElement("p");
  messageText.textContent = data.message;

  if (!isServerMessage) {
    const sendBy = document.createElement("div");
    sendBy.textContent = data.send_by;
    messageContentWrap.appendChild(sendBy);

    MessageItemBlockMain.appendChild(userProfileElement);
  }

  messageContentWrap.appendChild(messageText);

  MessageItemBlockMain.appendChild(messageContentWrap);

  messageChartContainer.appendChild(MessageItemBlockMain);
};
