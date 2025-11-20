# 🤝 CONTRIBUTING GUIDE
## How to Contribute to Pie Global Furniture

Thank you for your interest in contributing! This guide will help you get started.

---

## 📋 CODE OF CONDUCT

- Be respectful and professional
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

---

## 🚀 GETTING STARTED

### 1. Fork the Repository
```bash
# Click "Fork" on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/pie-global-furniture.git
cd pie-global-furniture
```

### 2. Set Up Development Environment
Follow the QUICKSTART.md guide to set up both backend and frontend.

### 3. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

---

## 💻 DEVELOPMENT WORKFLOW

### Making Changes

1. **Make small, focused commits**
   ```bash
   git add .
   git commit -m "feat: add product image gallery"
   ```

2. **Follow commit message conventions**
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation only
   - `style:` Code style (formatting)
   - `refactor:` Code refactoring
   - `test:` Adding tests
   - `chore:` Maintenance tasks

3. **Test your changes**
   ```bash
   # Backend
   python manage.py test
   
   # Frontend
   npm run lint
   npm run build
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Describe your changes
   - Reference any related issues

---

## 📝 CODING STANDARDS

### Python (Backend)
```python
# Good
def calculate_total_price(items: list[dict]) -> Decimal:
    """Calculate the total price of items in cart."""
    return sum(item['price'] * item['quantity'] for item in items)

# Use type hints
# Write docstrings
# Follow PEP 8
# Use descriptive names
```

### TypeScript (Frontend)
```typescript
// Good
interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

const calculateTotal = (items: CartItem[]): number => {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
};

// Use TypeScript
// Write interfaces
// Use const/let (not var)
// Use arrow functions
```

### CSS (Tailwind)
```jsx
// Good - Use Tailwind utilities
<button className="btn btn-primary hover:bg-primary-700 transition-colors">
  Click Me
</button>

// Avoid inline styles
// Use custom classes for repeated patterns
// Keep mobile-first approach
```

---

## 🧪 TESTING GUIDELINES

### Backend Tests
```python
from django.test import TestCase
from .models import Product

class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Sofa",
            price=999.99,
            category="sofa"
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Sofa")
        self.assertTrue(self.product.slug)
```

### Frontend Tests (Future)
```typescript
import { render, screen } from '@testing-library/react';
import ProductCard from './ProductCard';

test('renders product name', () => {
  render(<ProductCard name="Test Sofa" price={999} />);
  expect(screen.getByText('Test Sofa')).toBeInTheDocument();
});
```

---

## 📚 DOCUMENTATION

### Code Comments
```python
# Good comment - explains WHY
# Use slug lookup for SEO-friendly URLs instead of IDs
lookup_field = 'slug'

# Bad comment - explains WHAT (obvious)
# Set lookup field to slug
lookup_field = 'slug'
```

### Docstrings
```python
def get_featured_products(limit: int = 8) -> QuerySet:
    """
    Retrieve featured products for homepage.
    
    Args:
        limit: Maximum number of products to return (default: 8)
    
    Returns:
        QuerySet of Product objects marked as featured
    
    Example:
        products = get_featured_products(5)
    """
    return Product.objects.filter(featured=True, is_active=True)[:limit]
```

---

## 🐛 BUG REPORTS

### Before Reporting
- Check existing issues
- Try latest version
- Provide minimal reproduction

### Bug Report Template
```markdown
**Description:**
Brief description of the bug

**Steps to Reproduce:**
1. Go to...
2. Click on...
3. See error

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: Windows 11
- Browser: Chrome 120
- Python: 3.12
- Node: 18.17

**Screenshots:**
If applicable
```

---

## ✨ FEATURE REQUESTS

### Feature Request Template
```markdown
**Feature Description:**
Clear description of the feature

**Use Case:**
Why is this needed? Who will use it?

**Proposed Solution:**
How should it work?

**Alternatives Considered:**
Other approaches you thought about

**Additional Context:**
Mockups, examples, links
```

---

## 🔍 PULL REQUEST CHECKLIST

Before submitting:
- [ ] Code follows project style
- [ ] Tests pass
- [ ] New code has tests
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] PR description is complete
- [ ] Screenshots added (if UI change)

### PR Template
```markdown
**What does this PR do?**
Brief description

**Type of Change:**
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Related Issues:**
Fixes #123

**Screenshots:**
Before/After (if applicable)

**Checklist:**
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No console errors
```

---

## 🎯 AREAS TO CONTRIBUTE

### Easy (Good First Issues)
- Fix typos in documentation
- Add missing docstrings
- Improve error messages
- Add input validation
- Update dependencies

### Medium
- Add tests
- Create new UI components
- Improve existing features
- Add API endpoints
- Optimize queries

### Advanced
- Implement payment integration
- Add user authentication
- Build analytics dashboard
- Create mobile app
- Add real-time features

---

## 📖 RESOURCES

### Learn More
- [Django Docs](https://docs.djangoproject.com/)
- [React Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

### Project Docs
- README.md - Main documentation
- QUICKSTART.md - Setup guide
- SECURITY.md - Security practices
- DEPLOYMENT.md - Production deployment

---

## 💬 COMMUNICATION

### Where to Ask Questions
- GitHub Issues - Bug reports, feature requests
- GitHub Discussions - General questions
- Email - dev@yourdomain.com

### Response Times
- Bug reports: 24-48 hours
- Feature requests: 1 week
- Pull requests: 3-5 days

---

## 🎁 RECOGNITION

### Contributors
All contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Given public recognition

### Significant Contributions
Special recognition for:
- Major features
- Security improvements
- Performance optimizations
- Extensive documentation

---

## ⚖️ LICENSE

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

## 🙏 THANK YOU!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Questions?** Open an issue or email dev@yourdomain.com

**Happy coding! 🚀**
