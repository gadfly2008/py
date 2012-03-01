#!/usr/local/bin/python
# -*- coding: utf-8 -*-

Styles = {
    "definition": [
        {
            "name": "myBg",
            "type": "Animation",
            "param": "_alpha",
            "start": "0",
            "duration": "1"
        },
        {
            "name": "myDataLabelsFont",
            "type": "font",
            "font":"Verdana",
            "size": "10",
            "color": "435e4e",
            "bold": '1'
        },
        {
            "name": "myCaptionFont",
            "type": "font",
            "font":"Verdana",
            "size": "15",
            "color": "435e4e",
            "bold": "1"
        },
        {
            "name": "mySubCaptionFont",
            "type": "font",
            "font":"Verdana",
            "size": "10",
            "italic": "1",
            "color": "435e4e",
        },
        {
            "name": "myToolTipFont",
            "type": "font",
            "font":"Verdana",
            "size": "12",
            "color": "921a07",
        },
        {
            "name": "DataPlotShadow",
            "type": "Shadow",
            "distance": "6",
            "angle": "45",
            "quality": "4",
        }
    ],
    "application": [
        {
            "toobject": "DataPlot",
            "styles": "DataPlotShadow"
        },
        {
            "toobject": "BACKGROUND",
            "styles": "myBg"
        },
        {
            "toobject": "DATALABELS",
            "styles": "myDataLabelsFont"
        },
        {
            "toobject": "CAPTION",
            "styles": "myCaptionFont"
        },
        {
            "toobject": "SUBCAPTION",
            "styles": "mySubCaptionFont"
        },
        {
            "toobject": "TOOLTIP",
            "styles": "myToolTipFont"
        }
    ]
}

class StackedBar2D(object):
    def __init__(self, caption, subcaption):
        self._chart = {
            "caption": caption,
            "subcaption": subcaption,
            "useEllipsesWhenOverflow": "1",
            "borderColor": "98998f",
            "bgColor": "e3e7dd",
            "bgAlpha": "70",
            "canvasBgColor": "f4fefc",
            "canvasBgAlpha": "60",
            "canvasBorderColor": "a4a7a5",
            "plotBorderAlpha": "30",
            "numDivLines": "10",
            "legendShadow": "1",
            "formatNumber": "0",
            "formatNumberScale": "0",
            "chartLeftMargin": "10",
            "chartRightMargin": "0",
            "chartTopMargin": "10",
            "showShadow": "1",
            "showBorder": "1",
            "borderThickness": "1",
            "borderAlpha": "50",
            "overlapBars": "1",
            "alternateVGridColor": "dfe6e0",
            "valuePadding": "10",
            "showLegend": "1",
            "canvasRightMargin": "16",
            "showValues": "0",
            "stack100Percent": "1",
            "showPercentInToolTip": "1",
        }
        self._data = []

    def _get_chart(self):
        return self._chart
    def _set_chart(self, chart):
        self._chart = chart

    def _get_categories(self):
        return self._categories
    def _set_categories(self, categories):
        self._categories = categories

    def _get_dataset(self):
        return self._data
    def _set_dataset(self, data):
        self._data = data

    def to_dict(self):
        return {"chart": self.chart, "dataset": self.dataset, "categories": self.categories, "styles": Styles}

    chart = property(_get_chart, _set_chart)
    dataset = property(_get_dataset, _set_dataset)
    categories = property(_get_categories, _set_categories)

class StackedArea2D(object):
    def __init__(self, caption, subcaption):
        self._chart = {
            "caption": caption,
            "subcaption": subcaption,
            "useEllipsesWhenOverflow": "1",
            "borderColor": "98998f",
            "bgColor": "e3e7dd",
            "bgAlpha": "70",
            "canvasBgColor": "f4fefc",
            "canvasBgAlpha": "60",
            "canvasBorderColor": "a4a7a5",
            "plotBorderAlpha": "30",
            "numDivLines": "10",
            "legendShadow": "1",
            "formatNumber": "0",
            "formatNumberScale": "0",
            "chartLeftMargin": "10",
            "chartRightMargin": "10",
            "chartTopMargin": "10",
            "showShadow": "1",
            "showBorder": "1",
            "borderThickness": "1",
            "borderAlpha": "50",
            "overlapBars": "1",
            "alternateVGridColor": "dfe6e0",
            "valuePadding": "10",
            "showLegend": "1",
            "canvasRightMargin": "16",
            "showValues": "0",
        }
        self._data = []

    def _get_chart(self):
        return self._chart
    def _set_chart(self, chart):
        self._chart = chart

    def _get_categories(self):
        return self._categories
    def _set_categories(self, categories):
        self._categories = categories

    def _get_dataset(self):
        return self._data
    def _set_dataset(self, data):
        self._data = data

    def to_dict(self):
        return {"chart": self.chart, "dataset": self.dataset, "categories": self.categories, "styles": Styles}

    chart = property(_get_chart, _set_chart)
    dataset = property(_get_dataset, _set_dataset)
    categories = property(_get_categories, _set_categories)

class MSBar2D(object):
    def __init__(self, caption, subcaption):
        self._chart = {
            "caption": caption,
            "subcaption": subcaption,
            "useEllipsesWhenOverflow": "1",
            "borderColor": "98998f",
            "bgColor": "e3e7dd",
            "bgAlpha": "70",
            "canvasBgColor": "f4fefc",
            "canvasBgAlpha": "60",
            "canvasBorderColor": "a4a7a5",
            "plotBorderColor": "68849d",
            "plotFillAngle": "0",
            "numDivLines": "10",
            "legendShadow": "1",
            "defaultnumberscale": "Byte",
            "numberscalevalue": "1024,1024,1024,1024",
            "numberscaleunit": "K,M,G,T",
            "formatNumberScale": "1",
            "chartLeftMargin": "10",
            "chartRightMargin": "10",
            "chartTopMargin": "10",
            "showShadow": "1",
            "showBorder": "1",
            "borderThickness": "1",
            "borderAlpha": "50",
            "overlapBars": "1",
            "alternateVGridColor": "dfe6e0",
            "valuePadding": "10",
            "showLegend": "0",
            "canvasRightMargin": "16",
        }
        self._data = []

    def _get_chart(self):
        return self._chart
    def _set_chart(self, chart):
        self._chart = chart

    def _get_categories(self):
        return self._categories
    def _set_categories(self, categories):
        self._categories = categories

    def _get_dataset(self):
        return self._data
    def _set_dataset(self, data):
        self._data = data

    def to_dict(self):
        return {"chart": self.chart, "dataset": self.dataset, "categories": self.categories, "styles": Styles}

    chart = property(_get_chart, _set_chart)
    dataset = property(_get_dataset, _set_dataset)
    categories = property(_get_categories, _set_categories)

class ScrollComb2dDY(object):
    def __init__(self, caption, subcaption):
        self._chart = {
            "caption": caption,
            "subcaption": subcaption,
            "labelDisplay": "WRAP",
            "borderColor": "98998f",
            "bgColor": "e3e7dd",
            "bgAlpha": "70",
            "canvasBgColor": "f4fefc",
            "canvasBgAlpha": "76",
            "canvasBorderColor": "a4a7a5",
            "plotBorderColor": "002742",
            "plotFillAngle": "270",
            "scrollColor": "fbfafb",
            "numDivLines": "10",
            "legendShadow": "1",
            "defaultnumberscale": "Byte",
            "numberscalevalue": "1024,1024,1024,1024",
            "numberscaleunit": "KB,MB,GB,TB",
            "formatNumberScale": "1",
            "chartLeftMargin": "10",
            "chartRightMargin": "10",
            "chartTopMargin": "10",
            "yAxisValuesPadding": "6",
            "valuePadding": "6",
            "labelPadding": "8",
            "sFormatNumber": "0",
        }
        self._data = []

    def _get_chart(self):
        return self._chart
    def _set_chart(self, chart):
        self._chart = chart

    def _get_categories(self):
        return self._categories
    def _set_categories(self, categories):
        self._categories = categories

    def _get_dataset(self):
        return self._data
    def _set_dataset(self, data):
        self._data = data

    def to_dict(self):
        return {"chart": self.chart, "dataset": self.dataset, "categories": self.categories, "styles": Styles}

    chart = property(_get_chart, _set_chart)
    dataset = property(_get_dataset, _set_dataset)
    categories = property(_get_categories, _set_categories)

class Column3D(object):
    def __init__(self, caption, subcaption):
        self._chart = {
            "bgColor": "e3e7dd",
            "bgAlpha": "70",
            "canvasBgColor": "fbfdfe",
            "canvasBgAlpha": "90",
            "numDivLines": "10",
            "divLineColor": "d1ceb4",
            "formatNumber": "1",
            "showBorder": "1",
            "borderColor": "98998f",
            "showToolTipShadow": "1",
            "caption": caption,
            "subcaption": subcaption,
            "showShadow": "1",
            "maxColWidth": "60",
            "yAxisValuesPadding": "6",
            "labelPadding": "8",
            "valuePadding": "6",
            "chartLeftMargin": "10",
            "chartRightMargin": "10",
            "chartTopMargin": "10",
            "plotFillAlpha": "86",
            "defaultnumberscale": "Byte",
            "numberscalevalue": "1024,1024,1024,1024",
            "numberscaleunit": "KB,MB,GB,TB",
            "formatNumberScale": "1",
            "borderThickness": "1",
            "borderAlpha": "50",
            "palette": "5",
        }
        self._data = []

    def _get_chart(self):
        return self._chart

    def _set_chart(self, chart):
        self._chart = chart

    def _get_data(self):
        return self._data

    def _set_data(self, data):
        self._data = data

    def to_dict(self):
        return {"chart": self.chart, "data": self.data, "styles": Styles}

    chart = property(_get_chart, _set_chart)
    data = property(_get_data, _set_data)

class MSColumn3D(object):
    def __init__(self, caption, subcaption):
        self._chart = {
            "bgColor": "e3e7dd",
            "bgAlpha": "70",
            "canvasBgColor": "fbfdfe",
            "canvasBgAlpha": "90",
            "numDivLines": "10",
            "divLineColor": "d1ceb4",
            "formatNumber": "1",
            "showBorder": "1",
            "borderColor": "98998f",
            "showToolTipShadow": "1",
            "caption": caption,
            "subcaption": subcaption,
            "showShadow": "1",
            "maxColWidth": "60",
            "yAxisValuesPadding": "6",
            "labelPadding": "8",
            "valuePadding": "6",
            "chartLeftMargin": "10",
            "chartRightMargin": "10",
            "chartTopMargin": "10",
            "plotFillAlpha": "86",
            "defaultnumberscale": "Byte",
            "numberscalevalue": "1024,1024,1024,1024",
            "numberscaleunit": "KB,MB,GB,TB",
            "formatNumberScale": "1",
            "borderThickness": "1",
            "borderAlpha": "50",
            "palette": "5",
        }
        self._data = []

    def _get_chart(self):
        return self._chart
    def _set_chart(self, chart):
        self._chart = chart

    def _get_categories(self):
        return self._categories
    def _set_categories(self, categories):
        self._categories = categories

    def _get_dataset(self):
        return self._data
    def _set_dataset(self, data):
        self._data = data

    def to_dict(self):
        return {"chart": self.chart, "dataset": self.dataset, "categories": self.categories, "styles": Styles}

    chart = property(_get_chart, _set_chart)
    dataset = property(_get_dataset, _set_dataset)
    categories = property(_get_categories, _set_categories)

class Pie2D(object):
    def __init__(self, caption, subcaption):
        self._chart = {
            "bgcolor": "F4F4ED",
            "showBorder": "1",
            "toolTipBgColor": "f4f6de",
            "skipOverlapLabels": "1",
            "chartLeftMargin": "0",
            "chartRightMargin": "0",
            "chartTopMargin": "10",
            "captionPadding": "3",
            "showlegend": "1",
            "legendIconScale": "1.5",
            "legendBgColor": "fffdf9",
            "legendBgAlpha": "96",
            "legendBorderAlpha": "0",
            "legendShadow": "1",
            "formatNumber": "0",
            "formatNumberScale": "0",
            "enablesmartlabels": "1",
            "isSmartLineSlanted": "0",
            "smartLineColor": "e54f1d",
            "caption": caption,
            "subcaption": subcaption,
            "use3DLighting": "0",
            "showShadow": "0",
            "showPlotBorder": "1",
            "startingAngle": "78",
            "manageLabelOverflow": "1",
            "useEllipsesWhenOverflow": "1",
            "plotFillAlpha": "86",
            "plotBorderThickness": "1",
            "showValues": "1",
        }

    def _get_chart(self):
        return self._chart
    def _set_chart(self, chart):
        self._chart = chart

    def _get_data(self):
        return self._data
    def _set_data(self, data):
        self._data = data

    def to_dict(self):
        return {"chart": self._chart, "data": self._data, "styles": Styles}

    chart = property(_get_chart, _set_chart)
    data = property(_get_data, _set_data)

class MSLine2D(object):
    def __init__(self, caption, subcaption):
        self._chart = {
            "showShadow": "1",
            "caption": caption,
            "subcaption": subcaption,
            "showBorder": "1",
            "bgColor": "e3e7dd",
            "bgAlpha": "70",
            "canvasBgColor": "fbfdfe",
            "canvasBgAlpha": "90",
            "canvasBorderColor": "a4a7a5",
            "canvasBorderThickness": "1",
            "lineThickness": "2",
            "lineAlpha": "68",
            "drawAnchors": "1",
            "anchorRadius": "3",
            "anchorSides": "3",
            "numDivLines": "10",
            "divLineColor": "d1ceb4",
            "divLineThickness": "1",
            "legendShadow": "1",
            "formatNumber": "1",
            "defaultnumberscale": "Byte",
            "numberscalevalue": "1024,1024,1024,1024",
            "numberscaleunit": "KB,MB,GB,TB",
            "formatNumberScale": "1",
            "toolTipBgColor": "f4f6de",
            "showToolTipShadow": "1",
            "captionPadding": "10",
            "chartLeftMargin": "10",
            "chartRightMargin": "10",
            "chartTopMargin": "10",
            "canvasLeftMargin": "30",
            "canvasRightMargin": "30",
            "borderColor": "98998f",
            "borderThickness": "1",
            "borderAlpha": "50",
            "valuePadding": "3",
            "yAxisValuesPadding": "6",
            "labelPadding": "8",
            "showValues": "0",
        }

    def _get_chart(self):
        return self._chart

    def _set_chart(self, chart):
        self._chart = chart

    def _get_dataset(self):
        return self._dataset

    def _set_dataset(self, dataset):
        self._dataset = dataset

    def _get_categories(self):
        return self._categories

    def _set_categories(self, categories):
        self._categories = categories

    def to_dict(self):
        return {"chart": self._chart, "dataset": self._dataset, "categories": self._categories, "styles": Styles}

    chart = property(_get_chart, _set_chart)
    dataset = property(_get_dataset, _set_dataset)
    categories = property(_get_categories, _set_categories)

class MSCombiDY2D(object):
    def __init__(self, caption, subcaption):
        self._chart = {
            "showValues": "0",
            "setadaptiveymin": "1",
            "setadaptivesymin": "1",
            "linethickness": "1",
            "divlinecolor": "91AF46",
            "divlinealpha": "30",
            "yAxisValuesPadding": "6",
            "captionPadding": "8",
            "legendPadding": "15",
            "showalternatehgridcolor": "1",
            "numDivLines": "8",
            "bgColor": "e3e7dd",
            "canvasbordercolor": "666666",
            "canvasBorderAlpha": "30",
            "canvasBorderThickness": "1",
            "anchorRadius": "1",
            "plotBorderThickness": "1",
            "plotBorderAlpha": "20",
            "caption": caption,
            "subcaption": subcaption,
            "formatNumber": "1",
            "formatNumberScale": "1",
            "numberScaleValue": "1024,1024,1024,1024",
            "numberScaleUnit": "KB,MB,GB,TB",
            "sFormatNumber": "0",
            "borderColor": "98998f",
            "borderThickness": "1",
            "borderAlpha": "50",
            "labelPadding": "8",
            "valuePosition": "ABOVE",
            "valuePadding": "6",
        }

    def _get_chart(self):
        return self._chart

    def _set_chart(self, chart):
        self._chart = chart

    def _get_dataset(self):
        return self._dataset

    def _set_dataset(self, dataset):
        self._dataset = dataset

    def _get_categories(self):
        return self._categories

    def _set_categories(self, categories):
        self._categories = categories

    def to_dict(self):
        return {"chart": self._chart, "dataset": self._dataset, "categories": self._categories, "styles": Styles}

    chart = property(_get_chart, _set_chart)
    dataset = property(_get_dataset, _set_dataset)
    categories = property(_get_categories, _set_categories)