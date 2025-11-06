"use client";

import { motion } from "framer-motion";
import { CheckCircle, Clock, AlertCircle, Loader2, Server } from "lucide-react";
import { GradientCard } from "@/components/ui/gradient-card";
import { Badge } from "@/components/ui/badge";

interface ProgressHeaderProps {
  status: string;
  progress: number;
  jobId: string;
}

const statusConfig = {
  queued: {
    icon: Clock,
    label: "Queued",
    color: "text-foreground/60",
    bgColor: "bg-foreground/5",
    description: "Waiting to start processing",
  },
  running: {
    icon: Loader2,
    label: "Running",
    color: "text-primary",
    bgColor: "bg-primary/10",
    description: "Analyzing web pages and filtering content",
  },
  summarizing: {
    icon: Loader2,
    label: "Summarizing",
    color: "text-accent",
    bgColor: "bg-accent/10",
    description: "Generating quality metrics and statistics",
  },
  ready: {
    icon: CheckCircle,
    label: "Ready",
    color: "text-accent",
    bgColor: "bg-accent/10",
    description: "Preview complete - review results below",
  },
  failed: {
    icon: AlertCircle,
    label: "Failed",
    color: "text-danger",
    bgColor: "bg-danger/10",
    description: "Processing failed - contact support",
  },
};

export function ProgressHeader({ status, progress, jobId }: ProgressHeaderProps) {
  const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.queued;
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <GradientCard>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl ${config.bgColor}`}>
                <Icon className={`h-6 w-6 ${config.color} ${status === 'running' || status === 'summarizing' ? 'animate-spin' : ''}`} />
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-xl font-semibold">Benchmark Progress</h2>
                  <Badge variant="outline" className="text-xs">
                    <Server className="h-3 w-3 mr-1" />
                    Local Preview (1M pages)
                  </Badge>
                </div>
                <p className="text-sm text-foreground/60">{config.description}</p>
              </div>
            </div>

            <div className="text-right">
              <div className={`text-lg font-semibold ${config.color}`}>
                {config.label}
              </div>
              <div className="text-xs text-foreground/50">
                Job ID: {jobId.slice(0, 8)}...
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-foreground/70">Progress</span>
              <span className="font-medium">{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <motion.div
                className="bg-primary h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              />
            </div>
          </div>

          {/* Status Steps */}
          <div className="flex items-center justify-center gap-2">
            {Object.entries(statusConfig).slice(0, 4).map(([key, stepConfig], index) => {
              const isActive = key === status;
              const isCompleted = ['ready', 'failed'].includes(status) || (
                status === 'summarizing' && index < 2 ||
                status === 'running' && index < 1
              );

              return (
                <div key={key} className="flex items-center">
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full text-xs font-medium ${
                    isCompleted
                      ? 'bg-accent text-accent-foreground'
                      : isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle className="h-4 w-4" />
                    ) : (
                      index + 1
                    )}
                  </div>
                  {index < 3 && (
                    <div className={`w-8 h-0.5 mx-2 ${
                      isCompleted ? 'bg-accent' : 'bg-muted'
                    }`} />
                  )}
                </div>
              );
            })}
          </div>

          <div className="text-center">
            <p className="text-xs text-foreground/50">
              Processing ~1 million web pages • Usually completes in 5-10 minutes
            </p>
          </div>
        </div>
      </GradientCard>
    </motion.div>
  );
}
