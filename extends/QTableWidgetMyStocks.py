import sys, os, pprint, datetime;

from PyQt5 import QtWidgets, QtCore, QtGui;
from extends.QTableWidgetItemExtend import QTableWidgetItemExtend;

#Grid에서 선택된 Row에 배경,텍스트 색 지정
#(Draw시에 처리하는 함수라.. 속도 문제가 있을 수 있음)
#(또 Scroll 변경이 및 화면에 새로 그려질때마다 처리해서 성능 이슈가 있을 수 있음)
#(단 현재 사용중인 데이터 등록시 사용하는 FontColor를 Delegate로 이관하면.. 괜찮을 수 있음)
class ColorDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ColorDelegate, self).__init__(parent);

    def paint(self, painter, option, index):
        if index.data(QtCore.Qt.ForegroundRole) != None:
            option.palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(QtCore.Qt.lightGray));
            option.palette.setColor(QtGui.QPalette.HighlightedText, index.data(QtCore.Qt.ForegroundRole).color());
            QtWidgets.QStyledItemDelegate.paint(self, painter, option, index);

class QTableWidgetMyStocks(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super(QTableWidgetMyStocks, self).__init__(parent);
        super().setItemDelegate(ColorDelegate(self));
        self.parent = parent;
        self.setTabKeyNavigation(False);#Widget내부에서 Tab 이동 불가 설정(화살표 키로만 이동 가능)

    def initWidget(self, columns):
        keyCol = list(filter(lambda x: x.get("isKey", False) == True, columns));
        bgCol  = list(filter(lambda x: x.get("isBg" , False) == True, columns));

        try:
            if columns == None:
                raise Exception("{0}에 필수항목인 columns정보가 설정되지 않았습니다.".format(self.objectName()));
        
        except Exception as e:
            print(e);
            exit();
        
        if len(keyCol) == 0:
            _keyCol = {"id": "_id", "name": "keyCol", "type": str, "formatter": "{0}", "isKey": True};
            columns.insert(0, _keyCol);
            self.keyCol  = _keyCol;
        else:
            self.keyCol  = keyCol[0];
        
        for column in columns:
            if column.get("align", "") == "":
                if column["type"] in [int, float]:
                    column["align"] = QtCore.Qt.AlignRight;
                else:
                    column["align"] = QtCore.Qt.AlignLeft;
            
            if column.get("formatter", "") == "":
                if column["type"] in [int, float]:
                    column["formatter"] = "{0:,}";
                else:
                    column["formatter"] = "{0}";
                
        self.columns = columns;
        self.bgCol   = bgCol[0] if len(bgCol) != 0 else None;

        colNames = list(a["name"] for a in columns);
        self.setColumnCount(len(colNames));
        self.setHorizontalHeaderLabels(colNames);

        if self.keyCol["id"] == "_id":
            self.setColumnHidden(0, True);

        for idx, col in enumerate(self.columns):
            if "isVisible" in col:
                if not col["isVisible"]:
                    self.setColumnHidden(idx, True);
    
    #key값의 column Index를 조회
    def getColumnIdx(self, colId):
        colIds = [col["id"] for col in self.columns];
        return colIds.index(colId) if colId in colIds else None;

    #key값의 Row 데이터를 조회(key값이 없으면, 전체데이터 조회)
    def getRowDatas(self, key=None):
        rowDatas = [];

        if key != None:
            isExist = self.isExist(key);
        
            if isExist != None:
                data = {};
                for idx, col in enumerate(self.columns):
                    if col["type"] != QtWidgets.QPushButton:
                        data[col["id"]] = self.item(isExist.row(), idx).data(QtCore.Qt.UserRole);
                rowDatas.append(data);
        else:
            for row in range(self.rowCount()):
                data = {};
                for idx, col in enumerate(self.columns):
                    if col["type"] != QtWidgets.QPushButton:
                        data[col["id"]] = self.item(row, idx).data(QtCore.Qt.UserRole);
                rowDatas.append(data);

        return rowDatas;

    #열전체 데이터 조회
    def getColumnDatas(self, colId):
        colDatas = [];
        colIdx = self.getColumnIdx(colId);
        
        if colIdx != None:
            for row in range(self.rowCount()):
                colDatas.append(self.item(row, colIdx).data(QtCore.Qt.UserRole));
                                
        return colDatas;

    #정렬되어 있는 상태로 추가/수정 시 첫 Column은 이상이 없지만 두번째 컬럼 부터는 정렬안된 index값에 적용되는 경우가 있어
    #추가/수정시.. 먼저 정렬을 풀고, 로직 처리 후 다시 정렬을 활성화 하면 된다.
    def addRows(self, datas):
        if type(datas) == list:
            self.setSortingEnabled(False);
            
            for data in datas:
                if self.keyCol["id"] != "_id" and not self.keyCol["id"] in data:#key컬럼이 없으면 처리하지 않는다.
                    continue;
                
                if self.keyCol["id"] == "_id":
                    data["_id"] = str(-1);
                
                isExist = self.isExist(data[self.keyCol["id"]]);
                bgColor = self.getBgColor(data);

                if isExist == None:
                    #insert
                    rowNum = self.rowCount();
                    self.insertRow(rowNum);
                    
                    if self.keyCol["id"] == "_id":
                        data["_id"] = str(rowNum);
                    
                    for idx, col in enumerate(self.columns):
                        value = self.getDataColValue(col, data);

                        if col["type"] != QtWidgets.QPushButton:
                            iCol = QTableWidgetItemExtend(col["formatter"].format(value));
                            iCol.setData(QtCore.Qt.UserRole, value);
                            iCol.setTextAlignment(QtCore.Qt.AlignVCenter | col["align"]);
                            iCol.setForeground(QtGui.QBrush(QtGui.QColor(bgColor)));
                            self.setItem(rowNum, idx, iCol);
                        else:
                            iCol = QtWidgets.QPushButton(col.get("name", "btn"));
                            if col.get("slot", "") != "":
                                iCol.clicked.connect(lambda: col["slot"](data[self.keyCol["id"]]));
                            self.setCellWidget(rowNum, idx, iCol);
                else:
                    #update
                    for idx, col in enumerate(self.columns):
                        value = self.getDataColValue(col, data);
                        if col["type"] != QtWidgets.QPushButton:
                            iCol = self.item(isExist.row(), idx);
                            iCol.setText(col["formatter"].format(value));
                            iCol.setData(QtCore.Qt.UserRole, value);
                            iCol.setForeground(QtGui.QBrush(QtGui.QColor(bgColor)));
                        
            self.setSortingEnabled(True);
        elif type(datas) == dict:
            self.addRows([datas]);
    
    #데이터 화면 행을 삭제 하는 함수
    def delRows(self, datas):
        result = 0;
        if type(datas) == list:
            for key in datas:
                isExist = self.isExist(key);
                if isExist != None:
                    self.removeRow(isExist.row());
                    result = 1;
            return result;
        else:
            return self.delRows([datas]);
    
    #해당 ID 항목이 존재하는지 확인하는 함수
    def isExist(self, id):
        colIdx = self.getColumnIdx(self.keyCol["id"]);
        target = None;
        for row in range(self.rowCount()):
            if str(self.item(row, colIdx).data(QtCore.Qt.UserRole)) == str(id):
                target = self.item(row, colIdx);
                break;
        
        return target;

    def getBgColor(self, data):
        bgColor = "black";

        if self.bgCol != None:#TableWidget에 bgCol이 설정되어 있다면
            bgCol = None;

            if self.bgCol["id"] in data:#입력데이터에서 bgCol정보가 있다면
                bgCol = data[self.bgCol["id"]].replace(",", "") if type(data.get(self.bgCol["id"])) == str else data[self.bgCol["id"]];
            else:
                isExist    = self.isExist(data[self.keyCol["id"]]);
                colIdx     = self.getColumnIdx(self.bgCol["id"]);
                targetItem = self.item(isExist.row(), colIdx);
                #insertRow 실행시 bgCol보다 먼저 생성되는 항목들이 있으므로 None을 체크 한다.
                bgCol      = targetItem.data(QtCore.Qt.UserRole) if targetItem != None else bgCol;
            
            bgCol = 0 if bgCol == None else float(bgCol);
        
            bgColor = "red"   if bgCol >  0 else "blue";
            bgColor = "black" if bgCol == 0 else bgColor;
        return bgColor;

    def getDataColValue(self, col, data):
        value = None;
        
        if col["id"] in data:
            if col["type"] == type(data[col["id"]]):
                value = data[col["id"]];
            else:
                if col["type"] == str:
                    value = str(data[col["id"]]);
                elif col["type"] == bool:
                    value = True if str(data[col["id"]]).lower() == "true" else False;
                elif col["type"] == datetime.datetime:
                    value = data[col["id"]];
                elif col["type"] in [int, float]:
                    if data[col["id"]] == "":
                        value = 0;
                    else:
                        value = str(data[col["id"]]).replace(",", "");
                    value = col["type"](float(value));
                elif col["type"] in [QtWidgets.QPushButton]:
                    pass;
                else:
                    try:
                        raise Exception("처리할 수 없는 데이터 유형이 입력되었습니다.({0})".format(type(data[col["id"]]).__name__));
                    except Exception as e:
                        excp_type, excp_obj, excp_Tb = sys.exc_info();
                        fileName = os.path.split(excp_Tb.tb_frame.f_code.co_filename)[1];
                        print("{0}[line:{1}] - {2}".format(fileName, excp_Tb.tb_lineno, e));
        else:
            isExist = self.isExist(data[self.keyCol["id"]]);
            colIdx  = self.getColumnIdx(col["id"]);

            if self.item(isExist.row(), colIdx) != None:
                value = self.item(isExist.row(), colIdx).data(QtCore.Qt.UserRole);

        if value == None:
            if col["type"] == str:
                value = "";
            elif col["type"] == bool:
                value = False;
            elif col["type"] == datetime.datetime:
                value = datetime.datetime.now();
            elif col["type"] in [int, float]:
                value = 0;
            else:
                value = None;
        
        return value;

    """
    def resizeEvent(self, event):
        header     = self.horizontalHeader();
        headerSize = header.width();
        colSize    = [];
        hideCols   =  [x for x in range(10) if self.isColumnHidden(x) == True]

        #isColumnHidden 숨김컬럼 여부 확인 함수
        for column in range(header.count()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeToContents);
            if not self.isColumnHidden(column):
                colSize.append(max(header.sectionSize(column), header.defaultSectionSize()));
            else:
                colSize.append(0);

        diff, etc = divmod((headerSize - sum(colSize)), len(colSize) - len(hideCols));
        
        for column in range(header.count()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.Interactive);
            if headerSize > sum(colSize):
                header.resizeSection(column, colSize[column] + diff + (etc if column == range(header.count()) else 0));
            else:
                header.resizeSection(column, colSize[column]);
    """

if __name__ == "__main__":
    pass;