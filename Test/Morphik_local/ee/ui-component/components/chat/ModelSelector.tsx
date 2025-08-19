"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import { ChevronDown, Lock } from "lucide-react";
import { cn } from "@/lib/utils";
import { ModelConfigAPI } from "@/lib/modelConfigApi";
import { useModels } from "@/hooks/useModels";

interface Model {
  id: string;
  name: string;
  provider: string;
  description?: string;
}

interface ModelSelectorProps {
  apiBaseUrl: string;
  authToken: string | null;
  selectedModel?: string;
  onModelChange?: (modelId: string) => void;
  onRequestApiKey?: (provider: string) => void;
}

export function ModelSelector({
  apiBaseUrl,
  authToken,
  selectedModel,
  onModelChange,
  onRequestApiKey,
}: ModelSelectorProps) {
  const { models: serverModels, loading: loadingServerModels } = useModels(apiBaseUrl, authToken);
  const [currentModel, setCurrentModel] = useState<string>(selectedModel || "");
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Get saved API keys to determine which models are available
  const [availableProviders, setAvailableProviders] = useState<Set<string>>(new Set());
  const [customModels, setCustomModels] = useState<Model[]>([]);
  const [loadingCustomModels, setLoadingCustomModels] = useState(false);

  useEffect(() => {
    const loadAvailableProviders = async () => {
      const providers = new Set<string>();
      const api = new ModelConfigAPI(authToken);
      setLoadingCustomModels(true);

      try {
        // Get config from backend and localStorage
        const mergedConfig = await api.getMergedConfig();

        // Check which providers have API keys
        if (mergedConfig.openai?.apiKey) providers.add("openai");
        if (mergedConfig.anthropic?.apiKey) providers.add("anthropic");
        if (mergedConfig.google?.apiKey) providers.add("google");
        if (mergedConfig.groq?.apiKey) providers.add("groq");
        if (mergedConfig.deepseek?.apiKey) providers.add("deepseek");

        // DISABLED: Custom models loading - models already come from /models endpoint
        // This was causing duplicates
        /*
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/custom`, {
            headers: {
              Authorization: `Bearer ${authToken}`,
            },
          });

          if (response.ok) {
            const customModelsList = await response.json();
            console.log("Loaded custom models from backend:", customModelsList);

            const transformedCustomModels = customModelsList.map(
              (model: { id: string; name: string; provider: string; config: Record<string, unknown> }) => ({
                id: `custom_${model.id}`,
                name: model.name,
                provider: model.provider,
                description: `Custom ${model.provider} model`,
                config: model.config,
              })
            );
            console.log("Transformed custom models:", transformedCustomModels);
            setCustomModels(transformedCustomModels);

            // Add custom model providers
            customModelsList.forEach((model: { provider: string; config: { api_key?: string } }) => {
              // Check if the provider has an API key in the merged config
              // or if the model config contains an api_key
              if (mergedConfig[model.provider]?.apiKey) {
                providers.add(model.provider);
              } else if (
                model.config &&
                typeof model.config === "object" &&
                "api_key" in model.config &&
                model.config.api_key
              ) {
                // Model has its own API key
                providers.add(model.provider);
              }
            });
          }
        } catch (err) {
          console.error("Failed to load custom models from backend:", err);
        }
        */
      } catch (err) {
        console.error("Failed to load configurations:", err);

        // Fallback to localStorage
        const savedConfig = localStorage.getItem("morphik_api_keys");
        if (savedConfig) {
          try {
            const config = JSON.parse(savedConfig);

            if (config.openai?.apiKey) providers.add("openai");
            if (config.anthropic?.apiKey) providers.add("anthropic");
            if (config.google?.apiKey) providers.add("google");
            if (config.groq?.apiKey) providers.add("groq");
            if (config.deepseek?.apiKey) providers.add("deepseek");
          } catch (parseErr) {
            console.error("Failed to parse API keys:", parseErr);
          }
        }

        // Load custom models from localStorage
        const savedModels = localStorage.getItem("morphik_custom_models");
        if (savedModels) {
          try {
            const parsedModels = JSON.parse(savedModels);
            const transformedCustomModels = parsedModels.map(
              (model: { id: string; name: string; provider: string }) => ({
                id: `custom_${model.id}`,
                name: model.name,
                provider: model.provider,
                description: `Custom ${model.provider} model`,
              })
            );
            setCustomModels(transformedCustomModels);

            // Add custom model providers to available providers
            const config = JSON.parse(localStorage.getItem("morphik_api_keys") || "{}");
            parsedModels.forEach((model: { provider: string; config: { api_key?: string } }) => {
              if (config[model.provider]?.apiKey || model.config.api_key) {
                providers.add(model.provider);
              }
            });
          } catch (parseErr) {
            console.error("Failed to parse custom models:", parseErr);
          }
        }
      }

      // Check for OpenAI key in environment (from .env file)
      if (process.env.OPENAI_API_KEY || process.env.NEXT_PUBLIC_OPENAI_API_KEY) {
        providers.add("openai");
      }


      console.log("Final available providers:", Array.from(providers));
      setAvailableProviders(providers);
      setLoadingCustomModels(false);
    };

    if (isOpen) {
      loadAvailableProviders();
    }
  }, [isOpen, authToken]); // Re-check when dropdown opens

  // Combine server models with custom models
  const models = useMemo(() => {
    const allModels = [...serverModels, ...customModels];
    console.log("All models (server + custom):", allModels);
    return allModels;
  }, [serverModels, customModels]);

  // Handle initial model selection
  useEffect(() => {
    if (!currentModel && models.length > 0 && availableProviders.size > 0) {
      const firstAvailable = models.find(
        (m: Model) => isModelAvailable(m)
      );
      if (firstAvailable) {
        const modelId = firstAvailable.id;
        setCurrentModel(modelId);
        onModelChange?.(modelId);
      }
    }
  }, [models, currentModel, availableProviders, onModelChange]);

  const loading = loadingServerModels || loadingCustomModels;

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Define isModelAvailable function before it's used
  const isModelAvailable = (model: Model) => {
    console.log(`🔍 Checking model: ${model.id}, provider: ${model.provider}`);
    
    // Ollama модели всегда доступны
    if (model.id.startsWith("ollama_")) return true;
    
    // Custom модели всегда доступны  
    if (model.id.startsWith("custom_")) return true;
    
    // Проверяем по provider И по ID префиксу - ИСПРАВЛЕНЫ СКОБКИ!
    if ((model.id.startsWith("claude_") || (model.provider === "custom" && model.id.includes("claude"))) && availableProviders.has("anthropic")) return true;
    if ((model.id.startsWith("openai_") || model.provider === "openai") && availableProviders.has("openai")) return true;
    if ((model.id.startsWith("azure_") || (model.provider === "openai" && model.id.includes("azure"))) && availableProviders.has("azure")) return true;
    if ((model.id.startsWith("gemini_") || model.provider === "google") && availableProviders.has("google")) return true;
    if ((model.id.startsWith("groq_") || model.provider === "groq") && availableProviders.has("groq")) return true;
    if ((model.id.startsWith("deepseek_") || model.provider === "deepseek") && availableProviders.has("deepseek")) return true;
    
    console.log(`❌ Model ${model.id} not available - no provider key`);
    return false;
  };

  const handleModelSelect = (model: Model) => {
    if (isModelAvailable(model)) {
      setCurrentModel(model.id);
      onModelChange?.(model.id);
      setIsOpen(false);
    }
  };

  const providerIcons: Record<string, string> = {
    openai: "🟢",
    anthropic: "🔶",
    google: "🔵",
    groq: "⚡",
    deepseek: "🌊",
    configured: "⚙️",
    ollama: "🦙",
    together: "🤝",
    azure: "☁️",
  };

  const selectedModelData = models.find(m => m.id === currentModel);
  const displayName = currentModel === "default" ? "Morphik (default)" : selectedModelData?.name || "Select model";

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Current Model Display */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
        disabled={loading}
      >
        <span>{loading ? "Loading..." : displayName}</span>
        <ChevronDown className={cn("h-3 w-3 transition-transform", isOpen && "rotate-180")} />
      </button>

      {/* Dropdown */}
      {isOpen && !loading && (
        <div className="absolute bottom-full left-0 mb-2 w-72 rounded-lg border bg-popover p-1 shadow-lg">
          <div className="max-h-80 overflow-y-auto">
            {/* Default Morphik option */}
            <div
              className={cn(
                "group relative flex cursor-pointer items-start gap-2 rounded-md px-2 py-2 text-sm hover:bg-accent",
                currentModel === "default" && "bg-accent"
              )}
              onClick={() => {
                setCurrentModel("default");
                onModelChange?.("default");
                setIsOpen(false);
              }}
            >
              <span className="text-base">🤖</span>
              <div className="flex-1">
                <div className="flex items-center gap-1.5">
                  <span className="font-medium">Morphik (default)</span>
                </div>
              </div>
            </div>

            {models
              .filter(model => {
                const available = isModelAvailable(model);
                console.log(`Model ${model.id}: available=${available}, providers:`, Array.from(availableProviders));
                return available;
              })  // Only show available models
              .map(model => {
              const isAvailable = true; // We've already filtered, so all shown models are available
              console.log(`Showing model ${model.name} (${model.id}): provider=${model.provider}`);

              return (
                <div
                  key={model.id}
                  className={cn(
                    "group relative flex items-start gap-2 rounded-md px-2 py-2 text-sm",
                    "cursor-pointer hover:bg-accent",
                    currentModel === model.id && "bg-accent"
                  )}
                  onClick={() => handleModelSelect(model)}
                >
                  <span className="text-base">{providerIcons[model.provider] || "●"}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-1.5">
                      <span className="font-medium">{model.name}</span>
                    </div>
                    {model.description && <div className="text-xs text-muted-foreground">{model.description}</div>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
