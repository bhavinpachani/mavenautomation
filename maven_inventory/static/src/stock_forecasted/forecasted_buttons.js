/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ForecastedButtons } from "@stock/stock_forecasted/forecasted_buttons";
import { user } from "@web/core/user";
import { onWillStart } from "@odoo/owl";

patch(ForecastedButtons.prototype, {
    setup() {
        super.setup(...arguments);
        onWillStart(async () => {
            this.hasUpdateQtyGroup = await user.hasGroup(
                "maven_inventory.group_update_qty_onhand"
            );
        });
    },
});
