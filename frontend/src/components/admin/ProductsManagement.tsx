import React, { useEffect, useMemo, useState } from 'react';
import { Plus, Search, Pencil, Trash2, X, Upload, RefreshCw, ToggleLeft, ToggleRight } from 'lucide-react';
import { CATEGORIES, type Product } from '@/types';
import { useAdminProducts } from '@/hooks';
import { formatKSh } from '@/utils/helpers';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface ProductFormState {
  name: string;
  description: string;
  short_description: string;
  category: string;
  price: string;
  compare_at_price: string;
  stock: string;
  sku: string;
  dimensions: string;
  material: string;
  color: string;
  weight: string;
  featured: boolean;
  is_active: boolean;
  on_sale: boolean;
  meta_title: string;
  meta_description: string;
  main_image: File | null;
}

const emptyFormState: ProductFormState = {
  name: '',
  description: '',
  short_description: '',
  category: 'other',
  price: '',
  compare_at_price: '',
  stock: '0',
  sku: '',
  dimensions: '',
  material: '',
  color: '',
  weight: '',
  featured: false,
  is_active: true,
  on_sale: false,
  meta_title: '',
  meta_description: '',
  main_image: null,
};

const normalizeProductForForm = (product?: Product | null): ProductFormState => ({
  name: product?.name || '',
  description: product?.description || '',
  short_description: product?.short_description || '',
  category: product?.category || 'other',
  price: product?.price ? String(product.price) : '',
  compare_at_price: product?.compare_at_price ? String(product.compare_at_price) : '',
  stock: product?.stock !== undefined ? String(product.stock) : '0',
  sku: product?.sku || '',
  dimensions: product?.dimensions || '',
  material: product?.material || '',
  color: product?.color || '',
  weight: product?.weight || '',
  featured: !!product?.featured,
  is_active: product?.is_active ?? true,
  on_sale: !!product?.on_sale,
  meta_title: product?.meta_title || '',
  meta_description: product?.meta_description || '',
  main_image: null,
});

export const ProductsManagement: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [formState, setFormState] = useState<ProductFormState>(emptyFormState);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeletingId, setIsDeletingId] = useState<number | null>(null);

  const { products, loading, error, refetch, createProduct, updateProduct, deleteProduct } = useAdminProducts(
    true,
    0,
    100
  );

  useEffect(() => {
    void refetch(1, searchTerm || undefined, categoryFilter || undefined);
  }, [refetch, searchTerm, categoryFilter]);

  const filteredProducts = useMemo(() => products, [products]);

  const openCreateModal = () => {
    setEditingProduct(null);
    setFormState(emptyFormState);
    setPreviewUrl('');
    setIsModalOpen(true);
  };

  const openEditModal = (product: Product) => {
    setEditingProduct(product);
    setFormState(normalizeProductForForm(product));
    setPreviewUrl(product.main_image || '');
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingProduct(null);
    setFormState(emptyFormState);
    setPreviewUrl('');
  };

  const handleToggleField = async (product: Product, field: 'featured' | 'is_active' | 'on_sale') => {
    try {
      await updateProduct(product.id, { [field]: !product[field] });
      await refetch(1, searchTerm || undefined, categoryFilter || undefined);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (product: Product) => {
    const confirmed = window.confirm(`Delete ${product.name}? This cannot be undone.`);
    if (!confirmed) return;

    setIsDeletingId(product.id);
    try {
      await deleteProduct(product.id);
      await refetch(1, searchTerm || undefined, categoryFilter || undefined);
    } catch (err) {
      console.error(err);
    } finally {
      setIsDeletingId(null);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSaving(true);

    const payload: Record<string, any> = {
      ...formState,
      price: formState.price,
      compare_at_price: formState.compare_at_price || null,
      stock: Number(formState.stock || 0),
      main_image: formState.main_image,
    };

    try {
      if (editingProduct) {
        await updateProduct(editingProduct.id, payload);
      } else {
        await createProduct(payload);
      }

      closeModal();
      await refetch(1, searchTerm || undefined, categoryFilter || undefined);
    } catch (err) {
      console.error('Product save error:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleImageChange = (file: File | null) => {
    setFormState((prev) => ({ ...prev, main_image: file }));
    if (file) {
      const reader = new FileReader();
      reader.onload = () => setPreviewUrl(String(reader.result || ''));
      reader.readAsDataURL(file);
    } else {
      setPreviewUrl(editingProduct?.main_image || '');
    }
  };

  if (loading && !products.length) {
    return <LoadingSpinner fullScreen />;
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
        <p className="font-medium">Error loading products: {error}</p>
        <button
          onClick={() => void refetch(1, searchTerm || undefined, categoryFilter || undefined)}
          className="mt-2 font-medium underline"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Products Management</h2>
          <p className="text-gray-500 mt-1">Manage catalog items directly from the admin dashboard</p>
        </div>
        <button
          onClick={openCreateModal}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
        >
          <Plus size={16} />
          Add Product
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-white border border-gray-200 rounded-lg p-4">
        <div className="md:col-span-2 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search products by name, description, or SKU"
            className="w-full rounded-lg border border-gray-300 pl-10 pr-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        >
          <option value="">All Categories</option>
          {CATEGORIES.map((category) => (
            <option key={category.value} value={category.value}>
              {category.label}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, idx) => (
            <div key={idx} className="h-20 rounded-lg bg-white border border-gray-200 animate-pulse" />
          ))}
        </div>
      ) : filteredProducts.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 bg-white p-10 text-center text-gray-500">
          No products found.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Image</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Name</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Category</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Price</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Stock</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Units Sold</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Featured</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Active</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredProducts.map((product: any) => (
                <tr key={product.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="h-14 w-14 overflow-hidden rounded-lg border border-gray-200 bg-gray-100">
                      {product.main_image ? (
                        <img src={product.main_image} alt={product.name} className="h-full w-full object-cover" />
                      ) : null}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-semibold text-gray-900">{product.name}</p>
                      <p className="text-xs text-gray-500">SKU: {product.sku || '—'}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{product.category}</td>
                  <td className="px-4 py-3 font-semibold text-gray-900">{formatKSh(product.price)}</td>
                  <td className="px-4 py-3 text-gray-700">{product.stock}</td>
                  <td className="px-4 py-3 text-gray-700">{product.units_sold ?? 0}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleToggleField(product, 'featured')}
                      className="inline-flex items-center gap-1 text-sm font-medium text-gray-700 hover:text-blue-700"
                    >
                      {product.featured ? <ToggleRight className="text-green-600" size={20} /> : <ToggleLeft size={20} />}
                      {product.featured ? 'Yes' : 'No'}
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleToggleField(product, 'is_active')}
                      className="inline-flex items-center gap-1 text-sm font-medium text-gray-700 hover:text-blue-700"
                    >
                      {product.is_active ? <ToggleRight className="text-green-600" size={20} /> : <ToggleLeft size={20} />}
                      {product.is_active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openEditModal(product)}
                        className="inline-flex items-center gap-1 rounded-md border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-100"
                      >
                        <Pencil size={14} />
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(product)}
                        disabled={isDeletingId === product.id}
                        className="inline-flex items-center gap-1 rounded-md border border-red-200 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-50 disabled:opacity-60"
                      >
                        <Trash2 size={14} />
                        {isDeletingId === product.id ? 'Deleting…' : 'Delete'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4 py-6">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-2xl bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  {editingProduct ? 'Edit Product' : 'Create Product'}
                </h3>
                <p className="text-sm text-gray-500">Update product details and inventory</p>
              </div>
              <button onClick={closeModal} className="rounded-full p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6 px-6 py-6">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <label className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">Product Name</span>
                  <input
                    required
                    value={formState.name}
                    onChange={(e) => setFormState((prev) => ({ ...prev, name: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">Category</span>
                  <select
                    value={formState.category}
                    onChange={(e) => setFormState((prev) => ({ ...prev, category: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  >
                    {CATEGORIES.map((category) => (
                      <option key={category.value} value={category.value}>
                        {category.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">Price</span>
                  <input
                    required
                    type="number"
                    min="0"
                    step="0.01"
                    value={formState.price}
                    onChange={(e) => setFormState((prev) => ({ ...prev, price: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">Compare-at Price</span>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={formState.compare_at_price}
                    onChange={(e) => setFormState((prev) => ({ ...prev, compare_at_price: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">Stock</span>
                  <input
                    required
                    type="number"
                    min="0"
                    step="1"
                    value={formState.stock}
                    onChange={(e) => setFormState((prev) => ({ ...prev, stock: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">SKU</span>
                  <input
                    value={formState.sku}
                    onChange={(e) => setFormState((prev) => ({ ...prev, sku: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <label className="space-y-2 md:col-span-2">
                  <span className="text-sm font-medium text-gray-700">Short Description</span>
                  <input
                    value={formState.short_description}
                    onChange={(e) => setFormState((prev) => ({ ...prev, short_description: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>

                <label className="space-y-2 md:col-span-2">
                  <span className="text-sm font-medium text-gray-700">Description</span>
                  <textarea
                    rows={4}
                    value={formState.description}
                    onChange={(e) => setFormState((prev) => ({ ...prev, description: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <label className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">Dimensions</span>
                  <input
                    value={formState.dimensions}
                    onChange={(e) => setFormState((prev) => ({ ...prev, dimensions: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">Material</span>
                  <input
                    value={formState.material}
                    onChange={(e) => setFormState((prev) => ({ ...prev, material: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">Color</span>
                  <input
                    value={formState.color}
                    onChange={(e) => setFormState((prev) => ({ ...prev, color: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">Weight</span>
                  <input
                    value={formState.weight}
                    onChange={(e) => setFormState((prev) => ({ ...prev, weight: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <label className="space-y-2 md:col-span-2">
                  <span className="text-sm font-medium text-gray-700">Meta Title</span>
                  <input
                    value={formState.meta_title}
                    onChange={(e) => setFormState((prev) => ({ ...prev, meta_title: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>
                <label className="space-y-2 md:col-span-2">
                  <span className="text-sm font-medium text-gray-700">Meta Description</span>
                  <textarea
                    rows={3}
                    value={formState.meta_description}
                    onChange={(e) => setFormState((prev) => ({ ...prev, meta_description: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  />
                </label>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <label className="flex items-center gap-3 rounded-lg border border-gray-200 px-4 py-3">
                  <input
                    type="checkbox"
                    checked={formState.featured}
                    onChange={(e) => setFormState((prev) => ({ ...prev, featured: e.target.checked }))}
                    className="h-4 w-4"
                  />
                  <span className="text-sm font-medium text-gray-700">Featured</span>
                </label>
                <label className="flex items-center gap-3 rounded-lg border border-gray-200 px-4 py-3">
                  <input
                    type="checkbox"
                    checked={formState.is_active}
                    onChange={(e) => setFormState((prev) => ({ ...prev, is_active: e.target.checked }))}
                    className="h-4 w-4"
                  />
                  <span className="text-sm font-medium text-gray-700">Active</span>
                </label>
                <label className="flex items-center gap-3 rounded-lg border border-gray-200 px-4 py-3">
                  <input
                    type="checkbox"
                    checked={formState.on_sale}
                    onChange={(e) => setFormState((prev) => ({ ...prev, on_sale: e.target.checked }))}
                    className="h-4 w-4"
                  />
                  <span className="text-sm font-medium text-gray-700">On Sale</span>
                </label>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <label className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">Product Image</span>
                  <div className="flex items-center gap-3 rounded-lg border border-dashed border-gray-300 px-4 py-4">
                    <Upload size={16} className="text-gray-400" />
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => handleImageChange(e.target.files?.[0] || null)}
                      className="block w-full text-sm text-gray-600"
                    />
                  </div>
                </label>
                <div className="space-y-2">
                  <span className="text-sm font-medium text-gray-700">Preview</span>
                  <div className="flex h-32 items-center justify-center overflow-hidden rounded-lg border border-gray-200 bg-gray-50">
                    {previewUrl ? (
                      <img src={previewUrl} alt="Preview" className="h-full w-full object-cover" />
                    ) : (
                      <span className="text-sm text-gray-400">No image selected</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 border-t border-gray-200 pt-4">
                <button
                  type="button"
                  onClick={closeModal}
                  className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSaving}
                  className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                >
                  <RefreshCw size={16} className={isSaving ? 'animate-spin' : ''} />
                  {isSaving ? 'Saving...' : editingProduct ? 'Update Product' : 'Create Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductsManagement;
