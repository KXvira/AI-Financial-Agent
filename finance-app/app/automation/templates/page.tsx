'use client';

import { useState, useEffect } from 'react';
import { FileText, Plus, Edit, Trash2, Copy, Star, Grid, List, Download } from 'lucide-react';

interface Template {
  _id: string;
  name: string;
  description: string;
  category: string;
  is_default: boolean;
  is_public: boolean;
  sections: any[];
  layout: string;
  export_formats: string[];
  created_at: string;
  use_count: number;
}

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [categories, setCategories] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  useEffect(() => {
    fetchTemplates();
    fetchCategories();
  }, [selectedCategory]);

  const fetchTemplates = async () => {
    try {
      const url = selectedCategory === 'all'
        ? 'http://localhost:8000/automation/templates'
        : `http://localhost:8000/automation/templates?category=${selectedCategory}`;
      
      const response = await fetch(url);
      const data = await response.json();
      setTemplates(data.templates || []);
    } catch (error) {
      console.error('Error fetching templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:8000/automation/templates/categories/list');
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const deleteTemplate = async (templateId: string) => {
    if (!confirm('Are you sure you want to delete this template?')) return;

    try {
      const response = await fetch(`http://localhost:8000/automation/templates/${templateId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        fetchTemplates();
      } else {
        const data = await response.json();
        alert(data.detail || 'Failed to delete template');
      }
    } catch (error) {
      console.error('Error deleting template:', error);
      alert('Error deleting template');
    }
  };

  const duplicateTemplate = async (templateId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/automation/templates/${templateId}/duplicate`, {
        method: 'POST',
      });
      
      if (response.ok) {
        fetchTemplates();
      }
    } catch (error) {
      console.error('Error duplicating template:', error);
    }
  };

  const seedDefaults = async () => {
    try {
      await fetch('http://localhost:8000/automation/templates/seed/defaults', {
        method: 'POST',
      });
      fetchTemplates();
    } catch (error) {
      console.error('Error seeding defaults:', error);
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      financial: 'bg-blue-100 text-blue-800',
      receivables: 'bg-green-100 text-green-800',
      analytics: 'bg-purple-100 text-purple-800',
      custom: 'bg-gray-100 text-gray-800',
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Report Templates</h1>
            <p className="text-gray-600 mt-2">Create and manage custom report templates</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={seedDefaults}
              className="bg-gray-600 text-white px-6 py-3 rounded-lg flex items-center gap-2 hover:bg-gray-700 transition-colors"
            >
              <Download size={20} />
              Seed Defaults
            </button>
            <button
              className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors"
              onClick={() => alert('Template builder coming soon!')}
            >
              <Plus size={20} />
              Create Template
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Templates</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{templates.length}</p>
              </div>
              <FileText className="text-blue-600" size={40} />
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Default</p>
                <p className="text-3xl font-bold text-blue-600 mt-1">
                  {templates.filter(t => t.is_default).length}
                </p>
              </div>
              <Star className="text-blue-600" size={40} />
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Custom</p>
                <p className="text-3xl font-bold text-green-600 mt-1">
                  {templates.filter(t => !t.is_default).length}
                </p>
              </div>
              <FileText className="text-green-600" size={40} />
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Uses</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {templates.reduce((sum, t) => sum + t.use_count, 0)}
                </p>
              </div>
              <Download className="text-blue-600" size={40} />
            </div>
          </div>
        </div>

        {/* Filters and View Toggle */}
        <div className="flex justify-between items-center mb-6">
          <div className="flex gap-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedCategory === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              All
            </button>
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-lg transition-colors capitalize ${
                  selectedCategory === category
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {category}
              </button>
            ))}
          </div>

          <div className="flex gap-2 bg-white rounded-lg p-1 shadow">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${
                viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'
              }`}
            >
              <Grid size={20} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${
                viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'
              }`}
            >
              <List size={20} />
            </button>
          </div>
        </div>

        {/* Templates Grid/List */}
        {loading ? (
          <div className="text-center py-12">
            <FileText className="animate-pulse mx-auto mb-4 text-blue-600" size={60} />
            <p className="text-gray-600">Loading templates...</p>
          </div>
        ) : templates.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <FileText className="mx-auto mb-4 text-gray-400" size={60} />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Templates Found</h3>
            <p className="text-gray-600 mb-6">
              {selectedCategory === 'all'
                ? 'Create your first report template or seed the default templates'
                : `No templates found in the ${selectedCategory} category`}
            </p>
            <button
              onClick={seedDefaults}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg inline-flex items-center gap-2 hover:bg-blue-700"
            >
              <Download size={20} />
              Seed Default Templates
            </button>
          </div>
        ) : (
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
            {templates.map((template) => (
              <div
                key={template._id}
                className={`bg-white rounded-lg shadow hover:shadow-lg transition-shadow ${
                  viewMode === 'list' ? 'flex items-start p-6' : 'p-6'
                }`}
              >
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{template.name}</h3>
                        {template.is_default && (
                          <Star className="text-yellow-500" size={16} fill="currentColor" />
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(template.category)}`}>
                      {template.category}
                    </span>
                    {template.export_formats.map((format) => (
                      <span
                        key={format}
                        className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700"
                      >
                        {format.toUpperCase()}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                    <span>{template.sections.length} sections</span>
                    <span>{template.use_count} uses</span>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => alert('Edit functionality coming soon!')}
                      className="flex-1 bg-blue-100 text-blue-700 px-4 py-2 rounded-lg hover:bg-blue-200 transition-colors flex items-center justify-center gap-2"
                    >
                      <Edit size={16} />
                      Edit
                    </button>
                    <button
                      onClick={() => duplicateTemplate(template._id)}
                      className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
                      title="Duplicate"
                    >
                      <Copy size={16} />
                    </button>
                    {!template.is_default && (
                      <button
                        onClick={() => deleteTemplate(template._id)}
                        className="bg-red-100 text-red-700 px-4 py-2 rounded-lg hover:bg-red-200 transition-colors"
                        title="Delete"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Template Details */}
        {templates.length > 0 && (
          <div className="mt-8 bg-blue-50 border-l-4 border-blue-500 p-6 rounded">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">💡 About Templates</h3>
            <p className="text-blue-800">
              Report templates define the structure and content of your automated reports. Each template
              consists of sections (metrics, tables, charts) that pull data from your database. Default
              templates provide common financial reports, while custom templates let you create reports
              tailored to your specific needs.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
