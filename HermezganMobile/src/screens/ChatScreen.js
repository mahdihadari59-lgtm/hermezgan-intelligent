import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { addMessage, setTyping } from '../store/slices/chatSlice';
import chatService from '../services/chatService';

const ChatScreen = () => {
  const dispatch = useDispatch();
  const { messages, isTyping } = useSelector(state => state.chat);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollViewRef = useRef();

  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');

    dispatch(addMessage({
      text: userMessage,
      sender: 'user',
      timestamp: Date.now(),
    }));

    setIsLoading(true);
    dispatch(setTyping(true));

    try {
      const response = await chatService.sendMessage(userMessage, 'user123');
      
      dispatch(addMessage({
        text: response.response || 'پاسخ دریافت شد!',
        sender: 'bot',
        timestamp: Date.now(),
        suggestions: response.suggestions || [],
      }));
    } catch (error) {
      dispatch(addMessage({
        text: '❌ خطا در ارتباط با سرور',
        sender: 'bot',
        timestamp: Date.now(),
      }));
    } finally {
      setIsLoading(false);
      dispatch(setTyping(false));
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        ref={scrollViewRef}
        style={styles.messagesContainer}
        showsVerticalScrollIndicator={false}
      >
        {messages.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>🌊</Text>
            <Text style={styles.emptyTitle}>هرمزگان هوشمند</Text>
            <Text style={styles.emptySubtitle}>چطور می‌تونم کمکتون کنم؟</Text>
          </View>
        ) : (
          messages.map((msg, idx) => (
            <View
              key={idx}
              style={[
                styles.messageRow,
                msg.sender === 'user' ? styles.userRow : styles.botRow,
              ]}
            >
              <View
                style={[
                  styles.messageBubble,
                  msg.sender === 'user' ? styles.userMessage : styles.botMessage,
                ]}
              >
                <Text
                  style={[
                    styles.messageText,
                    msg.sender === 'user' ? styles.userText : styles.botText,
                  ]}
                >
                  {msg.text}
                </Text>
                {msg.suggestions && (
                  <View style={styles.suggestionsContainer}>
                    {msg.suggestions.map((s, i) => (
                      <TouchableOpacity key={i} style={styles.suggestionBtn}>
                        <Text style={styles.suggestionText}>{s}</Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                )}
              </View>
            </View>
          ))
        )}
        {isTyping && (
          <View style={styles.typingContainer}>
            <ActivityIndicator color="#667eea" />
          </View>
        )}
      </ScrollView>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          placeholder="پیام خود را بنویسید..."
          placeholderTextColor="#a0aec0"
          value={input}
          onChangeText={setInput}
          editable={!isLoading}
          multiline
        />
        <TouchableOpacity
          style={[styles.sendButton, isLoading && styles.sendButtonDisabled]}
          onPress={handleSendMessage}
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? (
            <ActivityIndicator color="white" size="small" />
          ) : (
            <Text style={styles.sendButtonText}>📤</Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8f9fa' },
  messagesContainer: { flex: 1, padding: 15 },
  emptyState: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: 100 },
  emptyIcon: { fontSize: 60 },
  emptyTitle: { fontSize: 20, fontWeight: 'bold', color: '#2d3748', marginTop: 20 },
  emptySubtitle: { fontSize: 14, color: '#a0aec0', marginTop: 10 },
  messageRow: { marginBottom: 12, flexDirection: 'row' },
  userRow: { justifyContent: 'flex-end' },
  botRow: { justifyContent: 'flex-start' },
  messageBubble: { maxWidth: '80%', padding: 12, borderRadius: 12 },
  userMessage: { backgroundColor: '#667eea' },
  botMessage: { backgroundColor: 'white', borderWidth: 1, borderColor: '#e9ecef' },
  messageText: { fontSize: 16, textAlign: 'right' },
  userText: { color: 'white' },
  botText: { color: '#2d3748' },
  suggestionsContainer: { marginTop: 8, flexDirection: 'row', flexWrap: 'wrap' },
  suggestionBtn: { backgroundColor: '#667eea20', padding: 6, borderRadius: 15, margin: 3 },
  suggestionText: { fontSize: 12, color: '#667eea' },
  typingContainer: { padding: 10, alignItems: 'center' },
  inputContainer: { flexDirection: 'row', padding: 12, backgroundColor: 'white', borderTopWidth: 1, borderTopColor: '#e9ecef' },
  textInput: { flex: 1, padding: 10, backgroundColor: '#f8f9fa', borderRadius: 20, marginRight: 8, textAlign: 'right', maxHeight: 100 },
  sendButton: { width: 44, height: 44, borderRadius: 22, backgroundColor: '#667eea', justifyContent: 'center', alignItems: 'center' },
  sendButtonDisabled: { opacity: 0.5 },
  sendButtonText: { fontSize: 20 },
});

export default ChatScreen;
