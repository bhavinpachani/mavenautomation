/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { Many2One } from "@web/views/fields/many2one/many2one";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";

/**
 * Global restriction for Many2one fields.
 *
 * When the current user belongs to a group with `restrict_many2one_create_edit`
 * enabled, this patch disables:
 *   - Quick Create (the "Create <name>" option in the dropdown)
 *   - Create and Edit (the "Create and edit..." option opening a form dialog)
 *   - Open/Edit link button (the arrow/external-link button next to the field)
 *
 * The restriction flag is passed from the backend via `session_info`.
 */

const isRestricted = session.restrict_many2one_create_edit || false;

// ---------------------------------------------------------------------------
// Patch Many2One component
// ---------------------------------------------------------------------------
// This controls the link button (open/edit) and the activeActions that are
// passed down to Many2XAutocomplete.
patch(Many2One.prototype, {
    /**
     * Override activeActions to disable create and createEdit when restricted.
     */
    get activeActions() {
        const actions = super.activeActions;
        if (isRestricted) {
            actions.create = false;
            actions.createEdit = false;
            actions.write = false;
        }
        return actions;
    },

    /**
     * Override many2XAutocompleteProps to disable quickCreate when restricted.
     */
    get many2XAutocompleteProps() {
        const props = super.many2XAutocompleteProps;
        if (isRestricted) {
            props.quickCreate = null;
        }
        return props;
    },

    /**
     * Override hasLinkButton to hide the open/edit button when restricted.
     * This prevents users from opening existing records for editing via M2O.
     */
    get hasLinkButton() {
        if (isRestricted) {
            return false;
        }
        return super.hasLinkButton;
    },

    /**
     * Override openRecord to prevent opening records when restricted.
     * Safety net in case the link button is triggered programmatically.
     */
    async openRecord(mode) {
        if (isRestricted) {
            return;
        }
        return super.openRecord(mode);
    },
});

// ---------------------------------------------------------------------------
// Patch Many2XAutocomplete component
// ---------------------------------------------------------------------------
// This controls the "Create", "Create and edit..." and "Search more..."
// dropdown options. We patch the suggestion methods to suppress creation
// options even if somehow activeActions still has them.
patch(Many2XAutocomplete.prototype, {
    /**
     * Never show the "Create <name>" quick-create suggestion when restricted.
     */
    addCreateSuggestion({ request }) {
        if (isRestricted) {
            return false;
        }
        return super.addCreateSuggestion({ request });
    },

    /**
     * Never show the "Create and edit..." suggestion when restricted.
     */
    addCreateEditSuggestion({ records, request }) {
        if (isRestricted) {
            return false;
        }
        return super.addCreateEditSuggestion({ records, request });
    },
});
