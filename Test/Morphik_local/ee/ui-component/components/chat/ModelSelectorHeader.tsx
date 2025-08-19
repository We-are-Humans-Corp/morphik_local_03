"use client";

import { useState, useEffect, useMemo } from "react";
import { ChevronDown, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useModels } from "@/hooks/useModels";
import { useMorphik } from "@/contexts/morphik-context";

interface Model {
  id: string;
  name: string;
  provider: string;
  description?: string;
}

interface ModelSelectorHeaderProps {
  currentModel: string;
  onModelChange: (modelId: string) => void;
}

export function ModelSelectorHeader({ currentModel, onModelChange }: ModelSelectorHeaderProps) {
  const { apiBaseUrl, authToken } = useMorphik();
  const { models: serverModels, loading } = useModels(apiBaseUrl, authToken);
  const [customModels, setCustomModels] = useState<Model[]>([]);

  // Load custom models from backend
  useEffect(() => {
    const fetchCustomModels = async () => {
      if (!authToken) return;
      
      try {
        const response = await fetch(`${apiBaseUrl}/model-config/custom-models/list`, {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        });

        if (response.ok) {
          const customModelsList = await response.json();
          const transformedCustomModels = customModelsList.map(
            (model: { id: string; name: string; provider: string }) => ({
              id: `custom_${model.id}`,
              name: model.name,
              provider: model.provider,
              description: `Custom ${model.provider} model`,
            })
          );
          setCustomModels(transformedCustomModels);
        }
      } catch (error) {
        console.error("Failed to fetch custom models:", error);
      }
    };

    fetchCustomModels();
  }, [apiBaseUrl, authToken]);

  // Combine all models
  const models = useMemo(() => {
    return [...serverModels, ...customModels];
  }, [serverModels, customModels]);

  // Find selected model
  const selectedModel = models.find(m => m.id === currentModel);
  const displayName = currentModel === "default" 
    ? "Default (Ollama)" 
    : selectedModel?.name || "Select model";

  // Provider icons
  const providerIcons: Record<string, string> = {
    ollama: "🦙",
    openai: "🟢",
    anthropic: "🔶",
    google: "🌈",
    groq: "⚡",
    deepseek: "🔍",
    azure: "☁️",
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          size="sm" 
          className="h-8 gap-1.5 px-3"
          disabled={loading}
        >
          <Sparkles className="h-3.5 w-3.5" />
          <span className="text-sm font-medium">{displayName}</span>
          <ChevronDown className="h-3.5 w-3.5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[250px]">
        <DropdownMenuItem onClick={() => onModelChange("default")}>
          <span className="mr-2">🤖</span>
          <span>Default (Ollama)</span>
        </DropdownMenuItem>
        
        {models.length > 0 && <DropdownMenuSeparator />}
        
        {models.map((model) => (
          <DropdownMenuItem
            key={model.id}
            onClick={() => onModelChange(model.id)}
            className={currentModel === model.id ? "bg-accent" : ""}
          >
            <span className="mr-2">
              {providerIcons[model.provider] || "●"}
            </span>
            <div className="flex flex-col">
              <span>{model.name}</span>
              {model.description && (
                <span className="text-xs text-muted-foreground">
                  {model.description}
                </span>
              )}
            </div>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}