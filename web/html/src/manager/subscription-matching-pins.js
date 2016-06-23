"use strict";

const React = require("react");
const {Table, Column, SearchField, Highlight, SimpleTableDataModel} = require("../components/tableng.js");
const StatePersistedMixin = require("../components/util").StatePersistedMixin;
const PopUp = require("../components/popup").PopUp;
const UtilComponent =  require("./subscription-matching-util");
const StrongText = UtilComponent.StrongText;
const SystemLabel = UtilComponent.SystemLabel;
const ToolTip = UtilComponent.ToolTip;
const humanReadablePolicy = UtilComponent.humanReadablePolicy;
const WarningIcon =  require("./subscription-matching-util").WarningIcon;
const Network = require("../utils/network");

const Pins = React.createClass({
  mixins: [StatePersistedMixin],

  getInitialState: function() {
    return {
        showPopUp: false,
        tableModel: new SimpleTableDataModel(this.buildRows(this.props))
    };
  },

  componentWillReceiveProps(nextProps) {
    if (this.props.pinnedMatches != nextProps.pinnedMatches ||
        this.props.subscriptions != nextProps.subscriptions ||
        this.props.systems != nextProps.systems ||
        this.props.subscriptions != nextProps.subscriptions
    ) {
        this.state.tableModel.mergeData(this.buildRows(nextProps));
        this.forceUpdate();
    }
  },

  rowComparator: function(aRaw, bRaw, columnKey) {
    const aValue = aRaw[columnKey];
    const bValue = bRaw[columnKey];

    var result = aValue.localeCompare(bValue);
    if (result == 0) {
      const aId = aRaw["id"];
      const bId = bRaw["id"];
      result = aId > bId ? 1 : (aId < bId ? -1 : 0);
    }

    return result;
  },

  buildRows: function(props) {
    const {pinnedMatches, systems, subscriptions} = props;

    return pinnedMatches.map((p) => {
      const system = systems[p.systemId];
      const systemName = system == null ? "System " + p.systemId : system.name;
      const systemType = system == null ? null : system.type;
      const subscription = subscriptions[p.subscriptionId];
      const subscriptionDescription = subscription == null ? "Subscription " + p.subscriptionId : subscription.description;
      const subscriptionPolicy = subscription == null ? " " : subscription.policy;
      const subscriptionEndDate = subscription == null ? " " : subscription.endDate;
      const subscriptionPartNumber = subscription == null ? "" : subscription.partNumber;

      return {
        id: p.id,
        systemId: p.systemId,
        systemName: systemName,
        systemType: systemType,
        subscriptionDescription: subscriptionDescription,
        subscriptionPolicy: subscriptionPolicy,
        subscriptionEndDate: subscriptionEndDate,
        subscriptionPartNumber: subscriptionPartNumber,
        status: p.status
      };
    });
  },

  onRemovePin: function(pinId) {
    Network.post("/rhn/manager/subscription-matching/pins/"+pinId+"/delete")
      .promise.then(data => this.props.onPinChanged(data));
  },

  showPopUp: function() {
    this.setState({showPopUp: true});
  },

  closePopUp: function() {
    this.setState({showPopUp: false});
  },

  savePin: function(systemId, subscriptionId) {
    Network.post("/rhn/manager/subscription-matching/pins", {system_id: systemId, subscription_id: subscriptionId})
      .promise.then(data => this.props.onPinChanged(data));
    $("#addPinPopUp").modal("hide"); //to trigger popup close action
    this.closePopUp();
  },


  render: function() {
    const popUpContent = this.state.showPopUp ? <AddPinPopUp products={this.props.products} systems={this.props.systems} subscriptions={this.props.subscriptions} onSavePin={this.savePin} /> : null;
    return (
      <div className="row col-md-12">
        <h2>{t("Pins")}</h2>
        <p>
          {t("You can pin a subscription to a system to suggest a certain association to the matching algorithm. ")}
          <br />
          {t("Next time a matching is attempted, the algorithm will try to produce a result that applies the subscription to the system you specified. ")}
          <br />
          {t("Note that the algorithm might determine that a certain pin cannot be respected, ")}
          {t("depending on a subscription's availablility and applicability rules, in that case it will be shown as not satisfied. ")}
        </p>

        {this.props.pinnedMatches.length > 0 ?
          <Table key="table"
            dataModel={this.state.tableModel}
            rowKeyFn={(row) => row.id}
            initialSort="systemName"
            >
            <Column
                columnKey="systemName"
                sortFn={this.rowComparator}
                header={t("Part number")}
                cell={ (p) => <SystemLabel id={p.systemId} name={p.systemName} type={p.systemType} /> }
                />
            <Column
                columnKey="subscriptionDescription"
                sortFn={this.rowComparator}
                header={t("Subscription")}
                cell={ (p) => p.subscriptionDescription }
                />
            <Column
                columnKey="subscriptionPolicy"
                sortFn={this.rowComparator}
                header={t("Policy")}
                cell={ (p) => humanReadablePolicy(p.subscriptionPolicy) }
                />
            <Column
                columnKey="subscriptionEndDate"
                sortFn={this.rowComparator}
                header={t("End date")}
                cell={ (p) => <ToolTip content={moment(p.subscriptionEndDate).fromNow()}
                                title={moment(p.subscriptionEndDate).format("LL")} /> }
                />
            <Column
                columnKey="subscriptionPartNumber"
                sortFn={this.rowComparator}
                header={t("Part number")}
                cell={ (p) => p.subscriptionPartNumber }
                />
            <Column
                columnKey="status"
                sortFn={this.rowComparator}
                header={t("Status")}
                cell={ (p) => <PinStatus status={p.status} /> }
                />
            <Column
                columnKey="actions"
                cell={ (p) => <PinButton
                      onClick={() => this.onRemovePin(p.id)}
                      content={<span><i className="fa fa-trash-o"></i>{t("Delete Pin")}</span>}
                      /> }
                />
          </Table>
          :
          <p>{t("No pins defined. You can create one with the button below.")}</p>}

        <button type="button" className="btn btn-primary" onClick={this.showPopUp} data-toggle="modal" data-target="#addPinPopUp">
          <i className="fa fa-plus"></i>{t("Add a Pin")}
        </button>
        <PopUp
          title={t("Add a Pin")}
          className="modal-lg"
          id="addPinPopUp"
          content={popUpContent}
          onClosePopUp={this.closePopUp}
        />
      </div>
    );
  }
});

const PinStatus = (props) => {
  if (props.status == "pending") {
    return <span><i className="fa fa-hourglass-start"></i><em>{t("pending next run")}</em></span>;
  }
  if (props.status == "satisfied") {
    return <span><i className="fa fa-check text-success"></i>{t("satisfied")}</span>;
  }
  return <span><WarningIcon />{t("not satisfied")}</span>;
}

const PinButton = (props) =>
  <button className="btn btn-default btn-cell" onClick={props.onClick}>
    {props.content}
  </button>
;

const AddPinPopUp = React.createClass({

  getInitialState:function() {
    return {
        systemId: null,
        tableModel: new SimpleTableDataModel(this.buildRows())
        };
  },

  componentWillReceiveProps(nextProps) {
    if (this.props.subscriptions != nextProps.subscriptions) {
        this.state.tableModel.mergeData(this.buildRows());
        this.forceUpdate();
    }
  },

  rowComparator: function(aRaw, bRaw, columnKey, ascending) {
    const aValue = aRaw[columnKey];
    const bValue = bRaw[columnKey];

    var result = 0;
    if (columnKey == "name") {
      result = aValue.localeCompare(bValue);
    }
    if (columnKey == "cpuCount") {
      result = aValue - bValue;
    }

    if (result == 0) {
      const aId = aRaw["id"];
      const bId = bRaw["id"];
      result = aId - bId;
    }
    return result;
  },

  buildRows: function() {
    return Object.keys(this.props.systems).map((id) => {
      return this.props.systems[id];
    });
  },

  onBackClicked: function () {
    this.setState({systemId: null});
  },

  onSystemSelected:function(systemId) {
    this.setState({systemId: systemId});
  },

  onSubscriptionSelected: function(subscriptionId) {
    this.props.onSavePin(this.state.systemId, subscriptionId);
  },

  searchData: function(data, criteria) {
    return data.filter((row) => row.name.toLowerCase().includes(criteria.toLowerCase()));
  },

  render: function() {
    var popUpContent;
    if (this.state.systemId == null) {
      popUpContent = (
        <div>
          <h4 className="add-pin-popup-subtitle">{t("Available Systems")}</h4>
          <p>{t("Step 1/2: select the system to pin from the table below.")}</p>

          <Table key="table"
            dataModel={this.state.tableModel}
            rowKeyFn={(row) => row.id}
            initialSort="name"
            searchPanel={
                <SearchField searchFn={this.searchData}
                    placeholder={t("Filter by name")}/>
            }>
            <Column
                columnKey="name"
                sortFn={this.rowComparator}
                header={t("System")}
                cell={ (s) => <SystemLabel id={s.id} name={s.name} type={s.type} /> }
                />
            <Column
                columnKey="cpuCount"
                sortFn={this.rowComparator}
                header={t("Socket/IFL count")}
                cell={ (s) => s.cpuCount }
                />
            <Column
                columnKey="products"
                header={t("Products")}
                cell={ (s) =>
                    <ProductTableCell key="products" products={this.props.products}
                        productIds={s.productIds} /> }
                />
            <Column
                columnKey="actions"
                cell={ (s) =>
                      <PinButton
                        onClick={() => this.onSystemSelected(s.id)}
                        content={<span>{t("Select")} <i className="fa fa-arrow-right fa-right"></i></span>}
                      /> }
                />
           </Table>

        </div>
      );
    }
    else {
      const system = this.props.systems[this.state.systemId];
      popUpContent = (
        <div>
          <h4 className="add-pin-popup-subtitle">{t("Available Subscriptions for the Selected System")}</h4>
          <p>{t("Step 2/2: pick a subscription for system ")}<strong>{system.name}</strong></p>
          <PinSubscriptionSelector onSubscriptionSelected={this.onSubscriptionSelected}
            subscriptions={system.possibleSubscriptionIds.map(
            p => this.props.subscriptions[p]
          )} />
          <p>
            <button className="btn btn-default" onClick={this.onBackClicked}>
              <i className="fa fa-arrow-left"></i>
              {t("Back to sytem selection")}
            </button>
          </p>
        </div>
      );
    }
    return (popUpContent);
  }
});

const ProductTableCell = (props) => {
  const productLength = props.productIds.length;

  if (productLength == 0){
    return <span/>;
  }

  const firstProductName = props.products[props.productIds[0]].productName;
  if (productLength == 1) {
    return <span>{firstProductName}</span>;
  }

  const productNames = props.productIds
    .map(i => props.products[i].productName)
    .reduce((previousValue, currentValue) => previousValue + ", " + currentValue);
  return (
      <ToolTip
        content={firstProductName + ", ..."}
        title={productNames}
      />
  );
};

const PinSubscriptionSelector = React.createClass({

  render: function() {
    if (this.props.subscriptions.length > 0) {
       return (
          <Table key="table"
            data={this.props.subscriptions}
            rowKeyFn={(row) => row.id}
            >
            <Column
                columnKey="partNumber"
                header={t("Part number")}
                cell={ (s) => s.partNumber }
                />
            <Column
                columnKey="description"
                header={t("Description")}
                cell={ (s) => s.description }
                />
            <Column
                columnKey="policy"
                header={t("Policy")}
                cell={ (s) => humanReadablePolicy(s.policy) }
                />
            <Column
                columnKey="endDate"
                header={t("End date")}
                cell={ (s) => <ToolTip content={moment(s.endDate).fromNow()}
                                  title={moment(s.endDate).format("LL")} /> }
                />
            <Column
                columnKey="actions"
                cell={ (s) => <PinButton
                          onClick={() => this.props.onSubscriptionSelected(s.id)}
                          content={<span><i className="fa fa-map-pin"></i>{t("Save Pin")}</span>}
                        /> }
                />
          </Table>);
    }
    else {
      return <p>{t("No subscriptions have been found to match this system, considering all products installed, either directly or in virtual guests.")}</p>
    }
  },
});

module.exports = {
  Pins: Pins,
}
