from django.db import models
from config.mixins.models import BaseModel
from authentication.models import User


class ChatHistory(BaseModel):
    """Chat History model, It will store the messages and response for login users only."""

    user = models.ForeignKey(
        User, related_name="chat_history", on_delete=models.CASCADE
    )

    message = models.TextField()
    response = models.TextField()

    class Meta:
        verbose_name = "Chat History"
        verbose_name_plural = "Chat History"

    def __str__(self):
        return f"{self.user} - {self.message[:50]}..."
