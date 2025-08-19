"use client";

import React, { createContext, useContext, useState, useCallback, useMemo } from "react";

interface ChatContextType {
  activeChatId: string | null;
  setActiveChatId: (id: string | null) => void;
  isChatVisible: boolean;
  setIsChatVisible: (visible: boolean) => void;
  isSettingsVisible: boolean;
  setIsSettingsVisible: (visible: boolean) => void;
  chatTitle: string;
  setChatTitle: (title: string) => void;
  canEditTitle: boolean;
  setCanEditTitle: (canEdit: boolean) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [isChatVisible, setIsChatVisible] = useState(true);
  const [isSettingsVisible, setIsSettingsVisible] = useState(false);
  const [chatTitle, setChatTitle] = useState("New Chat");
  const [canEditTitle, setCanEditTitle] = useState(false);

  const handleSetActiveChatId = useCallback((id: string | null) => {
    setActiveChatId(id);
    if (id) {
      // Reset title when switching chats
      setChatTitle("New Chat");
      setCanEditTitle(false);
    }
  }, []);

  const handleSetChatTitle = useCallback((title: string) => {
    setChatTitle(title);
  }, []);

  const value = useMemo(
    () => ({
      activeChatId,
      setActiveChatId: handleSetActiveChatId,
      isChatVisible,
      setIsChatVisible,
      isSettingsVisible,
      setIsSettingsVisible,
      chatTitle,
      setChatTitle: handleSetChatTitle,
      canEditTitle,
      setCanEditTitle,
    }),
    [
      activeChatId,
      handleSetActiveChatId,
      isChatVisible,
      isSettingsVisible,
      chatTitle,
      handleSetChatTitle,
      canEditTitle,
    ]
  );

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
}