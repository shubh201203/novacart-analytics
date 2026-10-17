import React from 'react';
import { FilterState, FilterOptions } from '../types/analytics';
import { RotateCcw, Calendar, MapPin, Tag } from 'lucide-react';

interface FilterBarProps {
  filters: FilterState;
  options: FilterOptions | null;
  onChange: (newFilters: FilterState) => void;
  onReset: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  options,
  onChange,
  onReset
}) => {
  const isFiltered = Boolean(filters.year || filters.month || (filters.region && filters.region !== 'All') || (filters.category && filters.category !== 'All'));

  return (
    <div className="bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-4 mb-6 shadow-md">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          {/* Year Filter */}
          <div className="flex items-center space-x-2 bg-[#0B132B]/80 px-3 py-1.5 rounded-lg border border-[#3A506B]/40">
            <Calendar size={14} className="text-[#48CAE4]" />
            <label className="text-xs font-semibold text-slate-400">Year:</label>
            <select
              value={filters.year || ''}
              onChange={(e) => onChange({ ...filters, year: e.target.value ? Number(e.target.value) : undefined })}
              className="bg-transparent text-sm font-medium text-white focus:outline-none cursor-pointer"
            >
              <option value="" className="bg-[#1C2541] text-white">All Years</option>
              {options?.years.map((y) => (
                <option key={y} value={y} className="bg-[#1C2541] text-white">
                  {y}
                </option>
              ))}
            </select>
          </div>

          {/* Month Filter */}
          <div className="flex items-center space-x-2 bg-[#0B132B]/80 px-3 py-1.5 rounded-lg border border-[#3A506B]/40">
            <Calendar size={14} className="text-[#48CAE4]" />
            <label className="text-xs font-semibold text-slate-400">Month:</label>
            <select
              value={filters.month || ''}
              onChange={(e) => onChange({ ...filters, month: e.target.value ? Number(e.target.value) : undefined })}
              className="bg-transparent text-sm font-medium text-white focus:outline-none cursor-pointer"
            >
              <option value="" className="bg-[#1C2541] text-white">All Months</option>
              {options?.months.map((m) => (
                <option key={m.num} value={m.num} className="bg-[#1C2541] text-white">
                  {m.name}
                </option>
              ))}
            </select>
          </div>

          {/* Region Filter */}
          <div className="flex items-center space-x-2 bg-[#0B132B]/80 px-3 py-1.5 rounded-lg border border-[#3A506B]/40">
            <MapPin size={14} className="text-[#48CAE4]" />
            <label className="text-xs font-semibold text-slate-400">Region:</label>
            <select
              value={filters.region || 'All'}
              onChange={(e) => onChange({ ...filters, region: e.target.value })}
              className="bg-transparent text-sm font-medium text-white focus:outline-none cursor-pointer"
            >
              <option value="All" className="bg-[#1C2541] text-white">All Regions</option>
              {options?.regions.map((r) => (
                <option key={r} value={r} className="bg-[#1C2541] text-white">
                  {r}
                </option>
              ))}
            </select>
          </div>

          {/* Category Filter */}
          <div className="flex items-center space-x-2 bg-[#0B132B]/80 px-3 py-1.5 rounded-lg border border-[#3A506B]/40">
            <Tag size={14} className="text-[#48CAE4]" />
            <label className="text-xs font-semibold text-slate-400">Category:</label>
            <select
              value={filters.category || 'All'}
              onChange={(e) => onChange({ ...filters, category: e.target.value })}
              className="bg-transparent text-sm font-medium text-white focus:outline-none cursor-pointer"
            >
              <option value="All" className="bg-[#1C2541] text-white">All Categories</option>
              {options?.categories.map((c) => (
                <option key={c} value={c} className="bg-[#1C2541] text-white">
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Reset Filter Button */}
        {isFiltered && (
          <button
            onClick={onReset}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/30 text-xs font-semibold hover:bg-rose-500/20 transition-all cursor-pointer"
          >
            <RotateCcw size={13} />
            <span>Clear Filters</span>
          </button>
        )}
      </div>
    </div>
  );
};
