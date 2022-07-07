#ifndef SPECIMEN_H
#define SPECIMEN_H

#include <QMainWindow>
#include <kebab.h>

QT_BEGIN_NAMESPACE
namespace Ui { class Specimen; }
QT_END_NAMESPACE

class Specimen : public QMainWindow
{
    Q_OBJECT

public:
    Specimen(QWidget *parent = nullptr);
    ~Specimen();

    void changeSauce(Kebab::Sauce sauce);

private:
    Ui::Specimen *ui;
    Kebab kebab;
};
#endif // SPECIMEN_H
