import React, { useState, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  addMessage,
  setLoading,
  setTyping,
} from '../../store/slices/chatSlice';
import chatService from '../../services/chatService';
import './MessageInput.css';

const MessageInput = () => {
  const dispatch = useDispatch();
  const { currentUser } = useSelector((state) => state.chat);

  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const handleSendMessage = async (e) => {
    e.preventDefault();

    const text = message.trim();

    if (!text) return;

    dispatch(
      addMessage({
        text,
        sender: 'user',
        avatar: currentUser.avatar,
      })
    );

    setMessage('');

    dispatch(setLoading(true));
    dispatch(setTyping(true));

    try {
      const response = await chatService.sendMessage(
        text,
        currentUser.id
      );

      await chatService.simulateTyping(1200);

      dispatch(
        addMessage({
          text:
            response.response ||
            'متأسفانه پاسخی دریافت نشد.',
          sender: 'bot',
          avatar: '🌊',
          location: response.location,
          suggestions: response.suggestions,
        })
      );
    } catch (error) {
      dispatch(
        addMessage({
          text: 'خطا در ارتباط با سرور.',
          sender: 'bot',
          avatar: '🌊',
        })
      );
    } finally {
      dispatch(setTyping(false));
      dispatch(setLoading(false));
    }
  };

  const handleVoiceStart = async () => {
    try {
      if (
        !navigator.mediaDevices ||
        !window.MediaRecorder
      ) {
        alert('مرورگر از ضبط صدا پشتیبانی نمی‌کند.');
        return;
      }

      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

      const recorder = new MediaRecorder(stream);

      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type: 'audio/webm',
          }
        );

        console.log(audioBlob);

        stream.getTracks().forEach((track) =>
          track.stop()
        );
      };

      recorder.start();

      setIsRecording(true);
    } catch (err) {
      console.error(err);
    }
  };

  const handleVoiceStop = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <form
      className="message-input-form"
      onSubmit={handleSendMessage}
    >
      <div className="input-wrapper">

        <button
          type="button"
          className={`input-btn voice-btn ${
            isRecording ? 'recording' : ''
          }`}
          onClick={
            isRecording
              ? handleVoiceStop
              : handleVoiceStart
          }
        >
          🎤
        </button>

        <input
          className="message-input"
          type="text"
          placeholder="پیام خود را بنویسید..."
          value={message}
          onChange={(e) =>
            setMessage(e.target.value)
          }
          disabled={isRecording}
        />

        <button
          type="submit"
          className="input-btn send-btn"
          disabled={!message.trim() || isRecording}
        >
          ➤
        </button>

      </div>
    </form>
  );
};

export default MessageInput;
