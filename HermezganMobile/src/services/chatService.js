const API_URL = 'https://hermezgan.ir/api/v1';

const chatService = {
  sendMessage: async (message, userId) => {
    try {
      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, user_id: userId }),
      });
      return await response.json();
    } catch (error) {
      return { response: 'خطا در ارتباط با سرور' };
    }
  },
};

export default chatService;
