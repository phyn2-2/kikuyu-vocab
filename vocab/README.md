# Vocab MVP
Inial setup for vocab module rebuild.

## Vocab Models 
This module defines the data models for a collaborative language learning platform.
Key features:
- Multi-language support (Kikuyu, English, Swahili)
- Approval workflow for user contributions
- Rich media support (audio, images)
- Social features (favorites, comments)
- Categorization and tagging system

## Vocab Admin - Interface
This module customizes the django admin interface for vocubulary management
Key Features:
- Visual media previews (audio player, image thumbnails)
- Quick approve/reject actions
- Smart filtering and search
- Status-based organization

## Vocab Views - Kikuyu Language Learning Platform
This module handles all public and contributor-facing views.

*View Hierarchy:*
- PUBLIC (no auth): Browse, search, detail view (approved words only)
- CONTRIBUTORS (auth): Add words, edit own submissions, favorite
- ADMIN: Full control via Django admin

*Performance Notes:*
- Uses select_related/prefetch_related to minimize database queries
- Implements pagination for large datasets
- Caches frequently accessed data

