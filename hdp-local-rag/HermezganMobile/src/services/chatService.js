const API_URL = 'http://127.0.0.1:8001/api/v1';

const chatService = {
  sendMessage: async (message, userId) => {
    try {
      const response = await fetch(`${API_URL}/chat/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: message }),
      });

      if (!response.ok) {
        return { response: `خطای سرور: ${response.status}` };
      }

      return await response.json();
    } catch (error) {
      console.error('Chat API error:', error);
      return { response: 'خطا در ارتباط با سرور' };
    }
  },
};

export default chatService;
