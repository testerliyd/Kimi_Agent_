import React, { useState, useRef, useEffect } from 'react';
import dayjs from 'dayjs';

interface GanttTask {
  id: string | number;
  name: string;
  startDate: string;
  endDate: string;
  progress: number;
  status: 'pending' | 'in_progress' | 'completed' | 'delayed';
  assignee?: string;
  color?: string;
}

interface GanttChartProps {
  tasks: GanttTask[];
  title?: string;
  onTaskClick?: (task: GanttTask) => void;
  onTaskUpdate?: (task: GanttTask) => void;
  editable?: boolean;
}

const statusColors: Record<string, string> = {
  pending: '#94a3b8',
  in_progress: '#22d3ee',
  completed: '#22c55e',
  delayed: '#ef4444',
};

const statusLabels: Record<string, string> = {
  pending: '待开始',
  in_progress: '进行中',
  completed: '已完成',
  delayed: '已延期',
};

export default function GanttChart({ 
  tasks, 
  title = '项目甘特图', 
  onTaskClick,
  onTaskUpdate,
  editable = false 
}: GanttChartProps) {
  const [viewMode, setViewMode] = useState<'day' | 'week' | 'month'>('week');
  const [selectedTask, setSelectedTask] = useState<GanttTask | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);

  // 计算时间范围
  const getDateRange = () => {
    if (tasks.length === 0) {
      const today = dayjs();
      return { start: today.subtract(7, 'day'), end: today.add(30, 'day') };
    }
    
    const dates = tasks.flatMap(t => [dayjs(t.startDate), dayjs(t.endDate)]);
    const minDate = dayjs.min(dates) || dayjs();
    const maxDate = dayjs.max(dates) || dayjs();
    
    return { 
      start: minDate.subtract(3, 'day'), 
      end: maxDate.add(7, 'day') 
    };
  };

  const { start, end } = getDateRange();
  const totalDays = end.diff(start, 'day');

  // 生成时间刻度
  const generateTimeScale = () => {
    const scale = [];
    let current = start.clone();
    
    while (current.isBefore(end) || current.isSame(end, 'day')) {
      if (viewMode === 'day') {
        scale.push({
          date: current.clone(),
          label: current.format('MM-DD'),
          isWeekend: current.day() === 0 || current.day() === 6,
        });
        current = current.add(1, 'day');
      } else if (viewMode === 'week') {
        scale.push({
          date: current.clone(),
          label: `W${current.week()}`,
          subLabel: current.format('MM-DD'),
          isWeekend: false,
        });
        current = current.add(1, 'week');
      } else {
        scale.push({
          date: current.clone(),
          label: current.format('YYYY-MM'),
          subLabel: current.format('MMM'),
          isWeekend: false,
        });
        current = current.add(1, 'month');
      }
    }
    return scale;
  };

  const timeScale = generateTimeScale();

  // 计算任务位置和宽度
  const getTaskStyle = (task: GanttTask) => {
    const taskStart = dayjs(task.startDate);
    const taskEnd = dayjs(task.endDate);
    const duration = Math.max(taskEnd.diff(taskStart, 'day'), 1);
    
    let startOffset, width;
    
    if (viewMode === 'day') {
      startOffset = taskStart.diff(start, 'day');
      width = duration;
    } else if (viewMode === 'week') {
      startOffset = taskStart.diff(start, 'day') / 7;
      width = Math.max(duration / 7, 0.5);
    } else {
      const monthDiff = (taskStart.year() - start.year()) * 12 + taskStart.month() - start.month();
      startOffset = monthDiff;
      width = Math.max(duration / 30, 0.3);
    }

    const unitWidth = viewMode === 'day' ? 50 : viewMode === 'week' ? 80 : 100;
    
    return {
      left: `${startOffset * unitWidth}px`,
      width: `${width * unitWidth}px`,
    };
  };

  const handleTaskClick = (task: GanttTask) => {
    setSelectedTask(task);
    onTaskClick?.(task);
  };

  const unitWidth = viewMode === 'day' ? 50 : viewMode === 'week' ? 80 : 100;

  return (
    <div className="gantt-chart bg-slate-900/60 rounded-lg border border-slate-700/50 overflow-hidden">
      {/* 标题栏 */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50 bg-gradient-to-r from-cyan-500/10 to-blue-500/10">
        <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          {title}
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-400">视图:</span>
          <div className="flex bg-slate-800 rounded-lg p-1">
            {(['day', 'week', 'month'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-3 py-1 text-sm rounded-md transition-all ${
                  viewMode === mode 
                    ? 'bg-cyan-500 text-white' 
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {mode === 'day' ? '日' : mode === 'week' ? '周' : '月'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 图例 */}
      <div className="flex items-center gap-4 px-4 py-2 border-b border-slate-700/50 bg-slate-800/30">
        <span className="text-sm text-slate-400">状态:</span>
        {Object.entries(statusLabels).map(([key, label]) => (
          <div key={key} className="flex items-center gap-1.5">
            <div 
              className="w-3 h-3 rounded-sm" 
              style={{ backgroundColor: statusColors[key] }}
            />
            <span className="text-xs text-slate-400">{label}</span>
          </div>
        ))}
      </div>

      {/* 甘特图主体 */}
      <div ref={chartRef} className="overflow-auto">
        <div className="min-w-max">
          {/* 时间刻度 */}
          <div className="flex border-b border-slate-700/50 bg-slate-800/50">
            <div className="w-48 flex-shrink-0 p-3 border-r border-slate-700/50 font-medium text-slate-300">
              任务名称
            </div>
            <div className="flex">
              {timeScale.map((item, index) => (
                <div 
                  key={index}
                  className={`flex-shrink-0 border-r border-slate-700/30 text-center py-2 text-xs ${
                    item.isWeekend ? 'bg-slate-800/50' : ''
                  }`}
                  style={{ width: `${unitWidth}px` }}
                >
                  <div className="text-slate-300 font-medium">{item.label}</div>
                  {item.subLabel && (
                    <div className="text-slate-500 text-[10px]">{item.subLabel}</div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 任务列表 */}
          <div className="relative">
            {tasks.length === 0 ? (
              <div className="p-8 text-center text-slate-500">
                <svg className="w-12 h-12 mx-auto mb-3 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p>暂无任务数据</p>
                <p className="text-sm mt-1">添加任务后将在此显示甘特图</p>
              </div>
            ) : (
              tasks.map((task, index) => {
                const style = getTaskStyle(task);
                const isSelected = selectedTask?.id === task.id;
                
                return (
                  <div 
                    key={task.id} 
                    className={`flex items-center border-b border-slate-700/30 hover:bg-slate-800/30 transition-colors ${
                      isSelected ? 'bg-cyan-500/10' : index % 2 === 0 ? 'bg-slate-900/20' : ''
                    }`}
                  >
                    {/* 任务信息 */}
                    <div className="w-48 flex-shrink-0 p-3 border-r border-slate-700/50">
                      <div className="text-sm text-slate-200 font-medium truncate">{task.name}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <span 
                          className="text-[10px] px-1.5 py-0.5 rounded"
                          style={{ 
                            backgroundColor: `${statusColors[task.status]}30`,
                            color: statusColors[task.status]
                          }}
                        >
                          {statusLabels[task.status]}
                        </span>
                        {task.assignee && (
                          <span className="text-[10px] text-slate-500">
                            {task.assignee}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* 任务条 */}
                    <div className="flex relative py-3" style={{ minWidth: `${timeScale.length * unitWidth}px` }}>
                      <div
                        className={`absolute h-7 rounded-md cursor-pointer transition-all hover:brightness-110 ${
                          editable ? 'cursor-grab active:cursor-grabbing' : ''
                        }`}
                        style={{
                          ...style,
                          backgroundColor: task.color || statusColors[task.status],
                          boxShadow: isSelected ? `0 0 10px ${task.color || statusColors[task.status]}50` : 'none',
                        }}
                        onClick={() => handleTaskClick(task)}
                      >
                        {/* 进度条 */}
                        <div 
                          className="h-full rounded-md bg-white/20"
                          style={{ width: `${task.progress}%` }}
                        />
                        
                        {/* 进度文字 */}
                        {parseInt(style.width) > 60 && (
                          <span className="absolute inset-0 flex items-center justify-center text-xs text-white font-medium">
                            {task.progress}%
                          </span>
                        )}
                      </div>

                      {/* 今天的标记线 */}
                      {viewMode === 'day' && (
                        <div 
                          className="absolute top-0 bottom-0 w-px bg-red-500/70 z-10"
                          style={{ 
                            left: `${dayjs().diff(start, 'day') * unitWidth}px` 
                          }}
                        >
                          <span className="absolute -top-1 -translate-x-1/2 text-[10px] text-red-400 bg-slate-900 px-1 rounded">
                            今天
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* 选中任务详情 */}
      {selectedTask && (
        <div className="border-t border-slate-700/50 p-4 bg-slate-800/50">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="text-sm font-medium text-slate-200">{selectedTask.name}</h4>
              <div className="flex items-center gap-4 mt-2 text-xs text-slate-400">
                <span>开始: {dayjs(selectedTask.startDate).format('YYYY-MM-DD')}</span>
                <span>结束: {dayjs(selectedTask.endDate).format('YYYY-MM-DD')}</span>
                <span>持续: {dayjs(selectedTask.endDate).diff(dayjs(selectedTask.startDate), 'day')} 天</span>
                <span>进度: {selectedTask.progress}%</span>
              </div>
            </div>
            <button 
              onClick={() => setSelectedTask(null)}
              className="text-slate-500 hover:text-slate-300"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
