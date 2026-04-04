"""Shared blog ORM field lists (schema before/after AI migration 0003)."""

# Columns present since blog.0001_initial — safe to SELECT when 0003 is not applied.
BLOG_POST_CORE_SELECT_FIELDS = (
    'id',
    'title',
    'slug',
    'excerpt',
    'body',
    'status',
    'published_at',
    'featured_image_url',
    'meta_title',
    'meta_description',
    'author_id',
    'created_at',
    'updated_at',
)
