import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useUserStore = create(
  persist(
    (set, get) => ({
      // Auth
      token: null,
      user: null,
      isAuthenticated: false,

      // Profile
      preferences: {
        notifications: true,
        voiceEnabled: true,
        autoRoute: false,
      },

      // Actions
      login: (token, user) =>
        set({ token, user, isAuthenticated: true }),

      logout: () =>
        set({
          token: null,
          user: null,
          isAuthenticated: false,
          preferences: {
            notifications: true,
            voiceEnabled: true,
            autoRoute: false,
          },
        }),

      setUser: (user) => set({ user }),
      setPreferences: (preferences) =>
        set((state) => ({
          preferences: { ...state.preferences, ...preferences },
        })),

      updatePreference: (key, value) =>
        set((state) => ({
          preferences: { ...state.preferences, [key]: value },
        })),
    }),
    {
      name: "hdp-user-store",
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        preferences: state.preferences,
      }),
    }
  )
);
